from __future__ import unicode_literals

from django.db import models
from datetime import date
# Create your models here.
class Mitra(models.Model):
	nama = models.CharField(max_length=50, unique=True)
	def __str__(self):
		return self.nama

class Barang(models.Model):
	nama_barang = models.CharField(max_length=25)
	harga = models.IntegerField(default=0)
	def __str__(self):
		return self.nama_barang

class BahanPembuatan(models.Model):
	SATUAN = (
		('g', 'Gram'),
		('kg', 'Kilo Gram'),
		('ml', 'Mili Liter'),
		)
	number = models.IntegerField(db_index=True)
	komposisi = models.DecimalField(max_digits=20, decimal_places=4, default=('0.000'))
	jumlah_satuan = models.CharField(max_length=3, choices=SATUAN, default='g')

	class Meta:
		abstract = True

class Bahan(BahanPembuatan):
	nama_barang = models.ForeignKey('Barang')
	nama_bahan = models.CharField(max_length=25)
	stok_jumlah = models.DecimalField(max_digits=20, decimal_places=4, default=('0.000'))
	def __str__(self):
		return self.nama_bahan

class Pemasukan(models.Model):
	tanggal = models.DateField(default=date.today)
	barang = models.ForeignKey('Barang')
	jumlah = models.IntegerField()
	tot_masuk = models.IntegerField()
	tujuan = models.ForeignKey('Mitra')

class Pengeluaran(models.Model):
	tanggal = models.DateField(default=date.today)
	bahan = models.ForeignKey('Bahan')
	jumlah = models.IntegerField(blank=False, null=False)
	tot_beli = models.IntegerField()
	satuan = models.CharField(max_length=15)

class Pembuatan(models.Model):
	nama_barang = models.ForeignKey('Bahan')
	nama_barang = Barang.nama_barang
	jumlah = models.IntegerField()