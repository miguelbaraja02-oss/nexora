from django.db import models

# -----------------------------
# 1️⃣ MODELO RACKS (antes pasillo)
# -----------------------------
class racks(models.Model):
    codigo = models.CharField(max_length=200, unique=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(max_length=200)
    estado = models.BooleanField(default=True)
    secciones_maximas = models.IntegerField(default=50)  # máximo de niveles permitidos

    def __str__(self):
        return f"Rack {self.codigo} - {self.titulo} (ID:{self.id})"


# -----------------------------
# 2️⃣ MODELO NIVELES (antes planta)
# -----------------------------
class niveles(models.Model):
    codigo = models.CharField(max_length=200, unique=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(max_length=200)
    estado = models.BooleanField(default=True)
    rack = models.ForeignKey(racks, null=True, on_delete=models.CASCADE, related_name="niveles")
    secciones_maximas = models.IntegerField(default=50)

    def __str__(self):
        return f"Nivel {self.codigo} ({self.rack.codigo if self.rack else 'Sin rack'}) (ID:{self.id})"


# -----------------------------
# 3️⃣ MODELO PROVEEDORES (antes proovedores)
# -----------------------------
class proveedores(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    telefono = models.TextField(max_length=200)
    correo = models.TextField(max_length=200)
    direccion = models.TextField(max_length=200)

    def __str__(self):
        return f"{self.nombre} (ID:{self.id})"


# -----------------------------
# 4️⃣ MODELO SECCIONES
# -----------------------------
class secciones1(models.Model):
    codigo = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField(max_length=200, blank=True)
    nivel = models.ForeignKey(niveles, null=False, on_delete=models.CASCADE, related_name="secciones")
    disponible = models.BooleanField(default=True)
    proveedor = models.ForeignKey(proveedores, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.codigo} - Nivel: {self.nivel.titulo} (ID:{self.id})"

    def save(self, *args, **kwargs):
        # ⚡ Generar código automáticamente solo si no se proporcionó
        if not self.codigo:
            total = secciones1.objects.filter(nivel=self.nivel).count() + 1
            self.codigo = f"{self.nivel.titulo}-S{total}"  # Ej: NIVEL1-S1, NIVEL1-S2
        super().save(*args, **kwargs)


# -----------------------------
# 5️⃣ MODELO UBICACIONES (antes ubicacion)
# -----------------------------
class ubicaciones(models.Model):
    codigo = models.CharField(max_length=200, unique=True)
    rack = models.ForeignKey(racks, null=False, on_delete=models.CASCADE)
    nivel = models.ForeignKey(niveles, null=False, on_delete=models.CASCADE)
    seccion = models.ForeignKey(secciones1, null=True, blank=True, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(proveedores, null=False, on_delete=models.CASCADE)
    descripcion_palet = models.TextField(max_length=200)
    disponible = models.BooleanField(default=True)
    # Nueva columna: cantidad de unidades en la ubicación (palets/ítems)
    cantidad = models.IntegerField(default=1)

    def __str__(self):
        return (
            f"Ubicación {self.codigo} - "
            f"Rack: {self.rack.codigo} (ID:{self.rack.id}) / "
            f"Nivel: {self.nivel.codigo} (ID:{self.nivel.id}) / "
            f"Sección: {self.seccion.codigo if self.seccion else 'Sin sección'} "
            f"(ID:{self.seccion.id if self.seccion else '-'})"
        )





