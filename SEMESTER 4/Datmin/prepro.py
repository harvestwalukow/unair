import pandas as pd
import typer
import re
from datetime import datetime

# Menstandarisasi kolom df
def kolom(df):
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()
    return df

# Memformat nomor telepon dengan hanya angka
def phone_number(phone):
    if pd.isna(phone):
        return None
    phone = re.sub(r'[^0-9]', '', str(phone))
    return phone if phone else None

# Memformat negara
def country(value, df=None):
    country_map = {
        "USA": "United States",
        "Usa": "United States",
        "US": "United States",
        "usa": "United States",
        "America": "United States",
        "CAN": "Canada",
        "FR": "France",
        "FRANCE": "France",
        "IND": "India",
        "Bharat": "India"
    }
    
    if pd.isna(value):
        return None
    
    if df is not None:
        if "country" in df.columns:
            column_name = "country"
        elif "nationality" in df.columns:
            column_name = "nationality"
        df[column_name] = df[column_name].apply(lambda x: country_map.get(x.strip(), x.strip()))
        return df
    else:
        return country_map.get(value.strip(), value.strip())

# Memformat nama
def name(df):
    if "name" in df.columns:
        df["name"] = df["name"].str.title()
    return df

# Memformat tanggal
def date(date_str):
    if pd.isna(date_str):
        return None
    
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", date_str)
    if match:
        year, month, day = map(int, match.groups())
        
        if month == 13 or day == 32:
            return datetime(year + 1, 1, 1).date()
    
    for fmt in ("%Y-%m-%d", "%b %d %Y", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    return None

# Memformat ID yang ada pada setiap data berdasarkan polanya
def id(df):
    if 'customerid' in df.columns and 'id' in df.columns:
        df['customerid'] = df.apply(
            lambda row: f"CUST_0{row['id']}" if 10 <= row['id'] < 100 else f"CUST_{row['id']}"
            if not isinstance(row['customerid'], str) or not row['customerid'].startswith("CUST_") 
            else row['customerid'], axis=1
        )
    
    if 'patientid' in df.columns:
        df['patientid'] = df['patientid'].apply(
            lambda x: f"PT_{int(re.sub(r'[^0-9]', '', str(x))):03d}" 
            if isinstance(x, str) else x
        )
    
    if 'citizenid' in df.columns and 'taxid' in df.columns:
        def format_taxid(taxid, citizenid):
            if pd.isna(taxid) or taxid.strip() == "":
                return "UNKNOWN"

            match = re.search(r'(\d+)', citizenid)
            if match:
                number = match.group()
                match_taxid = re.search(r'(\d{3})[^\d]*(\d{2})', taxid)
                if match_taxid:
                    return f"TAX-{match_taxid.group(1)}-{match_taxid.group(2)}"

            return "UNKNOWN"

        df['taxid'] = df.apply(lambda row: format_taxid(row['taxid'], row['citizenid']), axis=1)

    return df

# Mengisi missing values pada kolom product_category denga menggunakan metode forward fill dan backward fill
def product_category(df):
    if 'product_category' in df.columns and 'price' in df.columns:
        df['product_category'] = df['product_category'].replace("electornics", "electronics")
        df['original_index'] = df.index  

        df.sort_values(by='price', inplace=True)

        df['product_category'].fillna(method='ffill', inplace=True)
        df['product_category'].fillna(method='bfill', inplace=True)

        df.sort_values(by='original_index', inplace=True)
        df.drop(columns=['original_index'], inplace=True)
    return df

# Mengatasi missing values di kolom quantity
def quantity(df):
    if 'quantity' in df.columns:
        df['quantity'] = df['quantity'].fillna(df['quantity'].mean().round())
    return df

def address(address):
    if pd.isna(address):
        return None

    address = re.sub(r'[;]', ',', address)

    match = re.match(r'^(.*?),\s*(.*?),\s*([A-Z]{2})\s*(\d{5})$', address.strip())

    if match:
        street, city, state, zip_code = match.groups()
        return f"{street.strip()}, {city.strip()}, {state.strip()} {zip_code.strip()}"

    return address.strip()

# Menstandarisasi kolom votingstatus
def voting_status(df):
    if 'votingstatus' not in df.columns or 'nationality' not in df.columns:
        return df

    status_map = {
        "No": "Not Registered",
        "N": "Not Registered",
        "Yes": "Registered",
        "Y": "Registered",
        "Registered": "Registered"
    }

    def map_status(value):
        if pd.isna(value):
            return None
        value = str(value).strip()
        return status_map.get(value, None)

    df['votingstatus'] = df['votingstatus'].apply(map_status)

    mode_by_nationality = df.groupby('nationality')['votingstatus'].agg(lambda x: x.mode()[0] if not x.mode().empty else None)

    # Fill missing values berdasarkan modus nationality
    def fill_missing_status(row):
        if pd.isna(row['votingstatus']):
            return mode_by_nationality.get(row['nationality'], None)
        return row['votingstatus']

    df['votingstatus'] = df.apply(fill_missing_status, axis=1)

    return df

# Mengatasi missing values di kolom passportnumber
def passport_num(passport):
    if pd.isna(passport) or "INVALID_" in str(passport):
        return "UNKNOWN"
    return passport.strip()

# Menstandarisasi kolom maritalstatus
def marital_status(status):
    if pd.isna(status):
        return "UNKOWN"
    status = status.strip().lower()
    mapping = {
        "s": "Single",
        "single": "Single",
        "divorced": "Divorced",
        "married": "Married",
        "widowed": "Widowed",
        "unknown": "UNKNOWN"
    }
    return mapping.get(status, "Unknown")

# Mengatasi missing values dan standarisasi kolom criminalrecord
def criminal_record(record):
    if pd.isna(record) or str(record).strip().lower() in ["no", ""]:
        return "None"
    return record.strip()

# Standarisasi kolom educationlevel
def education_level(level):
    if pd.isna(level):
        return "UNKNOWN"
    level = level.strip().lower()
    mapping = {
        "hs": "High School",
        "high school": "High School",
        "bachelors": "Bachelors",
        "masters": "Masters",
        "phd": "PhD",
        "doctorate": "Doctorate"
    }
    return mapping.get(level, "Unknown")

# Mengisi baris kosong dengan "Undischarged"
def dischargedate(df):
    if 'dischargedate' in df.columns:
        df['dischargedate'] = df['dischargedate'].fillna("Undischarged")
    return df

# Melakukan standarisasi pada kolom diagnosis, department, dan doctor
def diagnosis_department_doctor(df):
    if 'diagnosis' not in df.columns or 'department' not in df.columns or 'doctor' not in df.columns:
        return df
    
    diagnosis_map = {
        'Appendycytys': 'Appendicitis',
        'Dyabetes': 'Diabetes',
        'Hypertensyon': 'Hypertension',
        'copd': 'COPD',
        'appendicitis': 'Appendicitis',
        'hypertension': 'Hypertension'
    }
    
    department_map = {
        'Cardilogy': 'Cardiology',
        'Cardio': 'Cardiology',
        'Endo': 'Endocrinology',
        'Ortho': 'Orthopedics'
    }
    
    df['diagnosis'] = df['diagnosis'].replace(diagnosis_map)
    df['department'] = df['department'].replace(department_map)
    df['diagnosis'] = df['diagnosis'].fillna('UNKNOWN')
    df['doctor'] = df['doctor'].fillna('UNKNOWN')
    df['department'] = df['department'].fillna('UNKNOWN')
    
    return df

# Mengatasi missing values dan standarisasi kolom age
def age(df):
    if 'age' in df.columns:
        df['age'] = df['age'].astype(str).str.replace('-', '', regex=True)
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
        df['age'] = df['age'].fillna(df['age'].mean().round())
    return df

# Menstandarisasi kolom gender
def gender(df):
    if 'gender' not in df.columns:
        return df
    
    gender_map = {
        'M': 'Male',
        'F': 'Female',
        'U': 'UNKNOWN'
    }
    
    df['gender'] = df['gender'].replace(gender_map)
    df['gender'] = df['gender'].fillna('UNKNOWN')

    return df

# Mengubah positive dan negative menjadi + dan -
def bloodtype(df):
    if 'bloodtype' in df.columns:
        df['bloodtype'] = df['bloodtype'].str.replace('positive', '+', regex=True)
        df['bloodtype'] = df['bloodtype'].str.replace('negative', '-', regex=True)
        df['bloodtype'] = df['bloodtype'].str.replace(' ', '', regex=True)
    return df

# Melakukan preprocessing
def preprocess_data(file_path: str):
    df = pd.read_csv(file_path)
    
    df = kolom(df)
    
    if 'phone_number' in df.columns:
        df['phone_number'] = df['phone_number'].apply(phone_number)
    for col in ["country", "nationality"]:
        if col in df.columns:
            df[col] = df[col].apply(country)
    if 'address' in df.columns:
        df['address'] = df['address'].apply(address)
    if 'votingstatus' in df.columns and 'nationality' in df.columns:
        df = voting_status(df)
    if 'passportnumber' in df.columns:
        df['passportnumber'] = df['passportnumber'].apply(passport_num)
    if 'maritalstatus' in df.columns:
        df['maritalstatus'] = df['maritalstatus'].apply(marital_status)
    if 'criminalrecord' in df.columns:
        df['criminalrecord'] = df['criminalrecord'].apply(criminal_record)
    if 'educationlevel' in df.columns:
        df['educationlevel'] = df['educationlevel'].apply(education_level)

    date_columns = [col for col in df.columns if 'date' in col]
    for col in date_columns:
        df[col] = df[col].apply(date)

    df = id(df)
    df = product_category(df)
    df = quantity(df)
    df = name(df)
    df = dischargedate(df)
    df = diagnosis_department_doctor(df)
    df = age(df)
    df = gender(df)
    df = bloodtype(df)

    df.to_csv("cleaned_" + file_path, index=False)
    print(f"Preprocessing selesai. Data yang bersih disimpan di cleaned_{file_path}")

def main(file_path: str):
    preprocess_data(file_path)

if __name__ == "__main__":
    typer.run(main)