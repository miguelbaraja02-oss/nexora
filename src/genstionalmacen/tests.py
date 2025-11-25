from django.test import TestCase
from django.urls import reverse

from .models import racks, niveles, proveedores, secciones1, ubicaciones


class SeguimientoTests(TestCase):
	def setUp(self):
		# Crear datos mínimos necesarios
		self.proveedor = proveedores.objects.create(
			nombre='PROV_TEST', telefono='777', correo='prov@test.local', direccion='Calle Test 1')

		self.rack = racks.objects.create(codigo='RACK-01', titulo='Rack 01', descripcion='Rack de prueba')

		self.nivel = niveles.objects.create(
			codigo='NIV-01', titulo='1', descripcion='Nivel 1', rack=self.rack
		)

		self.seccion = secciones1.objects.create(
			codigo='SEC-01', descripcion='Sección prueba', nivel=self.nivel, proveedor=self.proveedor
		)

		self.ubicacion = ubicaciones.objects.create(
			codigo='UBI-01',
			descripcion_palet='Palet de prueba',
			rack=self.rack,
			nivel=self.nivel,
			seccion=self.seccion,
			proveedor=self.proveedor,
			disponible=True
		)

	def test_ubicacion_relaciones(self):
		u = ubicaciones.objects.get(codigo='UBI-01')
		self.assertEqual(u.rack, self.rack)
		self.assertEqual(u.nivel, self.nivel)
		self.assertEqual(u.seccion, self.seccion)
		self.assertEqual(u.proveedor, self.proveedor)

	def test_seguimiento_view(self):
		url = reverse('seguimiento')
		resp = self.client.get(url)
		self.assertEqual(resp.status_code, 200)
		self.assertIn('ubicaciones', resp.context)
		qs = resp.context['ubicaciones']
		self.assertTrue(qs.filter(codigo='UBI-01').exists())
		# Verificar que el contenido renderizado incluya datos clave
		self.assertContains(resp, 'UBI-01')
		self.assertContains(resp, 'Palet de prueba')
		self.assertContains(resp, 'Rack 01')
