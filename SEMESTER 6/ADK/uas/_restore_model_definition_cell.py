import json
from pathlib import Path


path = Path("UAS_ADK_Multinomial_Logistic_CVD.ipynb")
notebook = json.loads(path.read_text(encoding="utf-8"))


def get_source(cell):
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


definition_source = """def softmax_baseline(X, B):
    eta = X @ B
    scores = np.column_stack([np.zeros(X.shape[0]), eta])
    scores -= scores.max(axis=1, keepdims=True)
    exp_scores = np.exp(scores)
    return exp_scores / exp_scores.sum(axis=1, keepdims=True)

def neg_loglik(X, y, B, l2=1e-6):
    P = softmax_baseline(X, B)
    eps = 1e-15
    penalty = 0.5 * l2 * np.sum(B[1:, :] ** 2)
    return -np.log(P[np.arange(len(y)), y] + eps).sum() + penalty

def hessian_baseline(X, P, l2=1e-6):
    n, p = X.shape
    K = P.shape[1]
    H = np.zeros((p * (K - 1), p * (K - 1)))
    for a in range(K - 1):
        for b in range(K - 1):
            pa = P[:, a + 1]
            pb = P[:, b + 1]
            w = pa * ((1 if a == b else 0) - pb)
            block = X.T @ (X * w[:, None])
            if a == b:
                reg = np.eye(p) * l2
                reg[0, 0] = 0
                block += reg
            H[a*p:(a+1)*p, b*p:(b+1)*p] = block
    return H

def fit_multinomial_logit(X, y, max_iter=80, tol=1e-7, l2=1e-6):
    n, p = X.shape
    classes = np.unique(y)
    K = len(classes)
    if not np.array_equal(classes, np.arange(K)):
        raise ValueError("y harus dikodekan 0 sampai K-1.")

    B = np.zeros((p, K - 1))
    Y = np.eye(K)[y][:, 1:]
    history = []

    for iteration in range(1, max_iter + 1):
        P = softmax_baseline(X, B)
        gradient = X.T @ (P[:, 1:] - Y)
        gradient[1:, :] += l2 * B[1:, :]
        H = hessian_baseline(X, P, l2=l2)

        grad_flat = gradient.T.reshape(-1)
        try:
            step_flat = np.linalg.solve(H, grad_flat)
        except np.linalg.LinAlgError:
            step_flat = np.linalg.pinv(H) @ grad_flat

        step = step_flat.reshape(K - 1, p).T
        current_loss = neg_loglik(X, y, B, l2=l2)
        step_scale = 1.0

        while step_scale > 1e-6:
            candidate = B - step_scale * step
            candidate_loss = neg_loglik(X, y, candidate, l2=l2)
            if candidate_loss <= current_loss:
                break
            step_scale *= 0.5

        B = candidate
        history.append(candidate_loss)

        if np.linalg.norm(step_scale * step) < tol:
            break

    P_final = softmax_baseline(X, B)
    H_final = hessian_baseline(X, P_final, l2=l2)
    try:
        covariance = np.linalg.inv(H_final)
    except np.linalg.LinAlgError:
        covariance = np.linalg.pinv(H_final)

    info = {
        "iterations": iteration,
        "loss": history[-1],
        "history": history,
        "covariance": covariance,
    }
    return B, info

def predict_multinomial(X, B):
    probabilities = softmax_baseline(X, B)
    predicted_class = probabilities.argmax(axis=1)
    return predicted_class, probabilities
"""


already_present = any(get_source(cell).startswith("def softmax_baseline(X, B):") for cell in notebook["cells"])

if not already_present:
    insert_at = next(
        i for i, cell in enumerate(notebook["cells"])
        if get_source(cell).startswith("B, fit_info = fit_multinomial_logit(X_all, y_all")
    )
    notebook["cells"].insert(
        insert_at,
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": definition_source,
        },
    )

path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1), encoding="utf-8")
