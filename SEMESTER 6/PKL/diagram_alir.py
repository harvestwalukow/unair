from graphviz import Digraph
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import io

g = Digraph('PKL_Flow', format='png')
g.attr(rankdir='TB', splines='ortho', nodesep='0.8', ranksep='1.2', fontname='Helvetica', 
        concentrate='false', center='true', margin='0.5')
g.attr('node', shape='box', style='rounded,filled', color='#333', fillcolor='white', 
        fontname='Helvetica', fontsize='10', width='2.5', height='0.8', fixedsize='true')

labels = {
    'n1':  "Pencarian informasi\ninstansi tujuan PKL",
    'n2':  "Pembuatan proposal\ndan surat permohonan PKL",
    'n3':  "Pengajuan proposal dan surat\npermohonan PKL ke pihak fakultas",
    'n4':  "Mengirim proposal dan surat\npermohonan PKL ke instansi tujuan",
    'n5':  "Pengumpulan data",
    'n6':  "Pendefinisian masalah dan\npencarian ide solusi",
    'n7':  "Pengenalan dan observasi\nlingkungan instansi",
    'n8':  "Mengisi formulir\npenerimaan PKL",
    'n9':  "Analisis data",
    'n10': "Penyampaian hasil analisis data\nkepada pihak instansi",
    'n11': "Penyusunan laporan\npelaksanaan PKL",
    'n12': "Seminar hasil PKL",
}
for k, v in labels.items():
    g.node(k, v)

# Row 1 (kiri → kanan)
with g.subgraph() as r1:
    r1.attr(rank='same')
    r1.edge('n1', 'n2')
    r1.edge('n2', 'n3')
    r1.edge('n3', 'n4')

# Row 2 (kiri → kanan)
with g.subgraph() as r2:
    r2.attr(rank='same')
    r2.edge('n5', 'n6')
    r2.edge('n6', 'n7')
    r2.edge('n7', 'n8')

# Row 3 (kiri → kanan)
with g.subgraph() as r3:
    r3.attr(rank='same')
    r3.edge('n9', 'n10')
    r3.edge('n10', 'n11')
    r3.edge('n11', 'n12')

# Konektor vertikal
g.edge('n4', 'n5')  # dari baris atas turun ke "Pengumpulan data" (kanan ke kiri)
g.edge('n5', 'n9')  # dari "Pengumpulan data" turun ke "Analisis data" (kiri ke kiri)

# Render ke bytes dan tampilkan dengan matplotlib
png_bytes = g.pipe(format='png')
img = Image.open(io.BytesIO(png_bytes))

# Tampilkan gambar
plt.figure(figsize=(14, 10))
plt.imshow(img)
plt.axis('off')
plt.title('Diagram Alir PKL', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.subplots_adjust(top=0.95)
plt.show()