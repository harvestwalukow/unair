Laporan Praktikum
Harvest Walukow
164231104

Masuk pada database classicmodels
USE classicmodels;


VIEWS
1. Data lengkap Customer yang paling berkontribusi dalam payment

CREATE VIEW customer_amount_terbanyak AS
SELECT * FROM customers
WHERE customers.customerNumber = (
SELECT customerNumber FROM payments
GROUP BY customerNumber
ORDER BY SUM(amount) DESC
LIMIT 1
);

Di buat view dari query untuk mengambil customerNumber yang amount payments-nya paling banyak, lalu ditampilkan semua data customer tersebut dari tabel customers.


2. Tampilkan customer.city, dan nilai maksimal pembelian

CREATE VIEW city_amount_max AS
SELECT city, MAX(amount) FROM customers JOIN payments
ON customers.customerNumber = payments.customerNumber
GROUP BY city;

Dibuat view dari query yang menggabungkan tabel customers dan payments, kemudian ditampilkan nama city-nya dan nilai amount maksimum di tiap kota setelah dikelompokkan kota-nya.


3. Tampilkan jumlah customer yang ditangani setiap employee

CREATE VIEW total_customer_employee AS
SELECT firstName, lastName, COUNT(customerNumber) FROM customers
JOIN employees
ON customers.salesRepEmployeeNumber = employees.employeeNumber
GROUP BY employeeNumber;

Dibuat view dari query yang menggabungkan tabel customers dan employees, lalu ditampilkan nama employee-nya dan jumlah customer yang ditangani setelah dilakukan pengelompokkan berdasarkan empoyeeNumber.


4. Tampilkan seluruh nama customer yang memiliki jumlah pembelian terkecil

CREATE VIEW nama_customer_amount_terkecil AS
SELECT customerName FROM customers WHERE customerNumber = (
SELECT customerNumber FROM payments WHERE amount = (
SELECT MIN(amount) FROM payments
)
);

Dibuat view dari query yang menggunakan beberapa nested query, di mana query yang pertama untuk mengambil nilai amount terkecil dari tabel payments, nilai itu lalu digunakan untuk query kedua untuk mendapatkan customerNumber yang melakukan pembelian terkecil tersebut. Lalu, ditampilkan nama customer dengan pembelian terkecil tersebut.


STORED PROCEDURES
1. Menambah stok produk dengan parameter productcode dan jumlah stok
DELIMITER //

CREATE PROCEDURE tambah_stok_produk(
    IN productCode VARCHAR(16),
    IN quantity INT
)
BEGIN
    UPDATE products
    SET quantityInStock = quantityInStock + quantity
    WHERE productCode = productCode
END //

CALL tambah_stok_produk("S10_1678", 7);


Setelah query dijalankan terjadi penambahan stok untuk kode produk tersebut:


2. Menambah Customer baru dengan parameter yang sesuai



3. Menambah payment baru dengan parameter yang sesuai


TRIGGER
1. Mengurangi stok produk tertentu setiap ada order masuk (sesuai kuantitas produk)


2. Membuat record baru dalam tabel baru (BarangHabis (productCode, dateHabis))
setiap ada barang yang stoknya habis


3. Menghapus record dalam tabel BarangHabis ketika ada stok baru dalam sebuah
produk tertentu

