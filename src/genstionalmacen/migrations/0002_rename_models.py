# genstionalmacen/migrations/0002_rename_models.py
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('genstionalmacen', '0001_initial'),  # Cambia esto si tu migración inicial tiene otro nombre
    ]

    operations = [
        # Renombrar modelos existentes a los nuevos nombres en minúscula
        migrations.RenameModel(
            old_name='pasillo',
            new_name='racks',
        ),
        migrations.RenameModel(
            old_name='planta',
            new_name='niveles',
        ),
        migrations.RenameModel(
            old_name='proovedores',
            new_name='proveedores',
        ),
        migrations.RenameModel(
            old_name='secciones',
            new_name='secciones1',
        ),
        migrations.RenameModel(
            old_name='ubicacion',
            new_name='ubicaciones',
        ),
    ]
