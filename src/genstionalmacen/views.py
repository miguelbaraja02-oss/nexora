from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import racks, niveles, proveedores, secciones1, ubicaciones
from django.db import transaction
import os
import requests

# -----------------------------
# VISTA PRINCIPAL
# -----------------------------
def index(request):
    listas_ubicaciones = ubicaciones.objects.all()
    context = {
        "listas_ubicaciones": listas_ubicaciones,
        # API keys must NOT be exposed to the frontend. Backend will proxy requests.
    }
    return render(request, 'index.html', context)



def eliminar_todo(request):
    # Verifica si hay datos antes de eliminar
    hay_datos = (
        racks.objects.exists() or
        niveles.objects.exists() or
        secciones1.objects.exists() or
        proveedores.objects.exists()
    )

    if not hay_datos:
        # Si no hay datos, mostrar mensaje en el panel
        return render(request, "panel_control.html", {"sin_datos": True})

    if request.method == "POST":
        racks.objects.all().delete()
        niveles.objects.all().delete()
        secciones1.objects.all().delete()
        proveedores.objects.all().delete()
        messages.success(request, "✅ Todos los registros fueron eliminados correctamente.")
        return redirect("panel_control")

    # Si es GET, mostrar confirmación
    return render(request, "panel_control.html", {"mostrar_confirmacion": True})








from django.views.decorators.csrf import csrf_exempt
import json

# -----------------------------
# CREAR RACK
# -----------------------------
def crear_rack(request):
    if request.method == "POST":
        codigo = (request.POST.get("codPasillo") or "").strip()
        titulo = (request.POST.get("nomPasillo") or "").strip()
        descripcion = (request.POST.get("descPasillo") or "").strip()
        activo = True if request.POST.get("check") == "on" else False

        # Validaciones básicas
        if not codigo or not titulo:
            messages.error(request, "Debe ingresar código y nombre del rack.")
            return redirect("crear_rack")

        if racks.objects.filter(codigo=codigo).exists():
            messages.error(request, f"El rack con código '{codigo}' ya existe.")
            return redirect("crear_rack")
        if racks.objects.filter(titulo=titulo.upper()).exists():
            messages.error(request, f"El título '{titulo}' ya existe.")
            return redirect("crear_rack")

        racks.objects.create(
            codigo=codigo,
            titulo=titulo.upper(),
            descripcion=descripcion.upper()
        )
        messages.success(request, f"Rack '{titulo.upper()}' creado exitosamente!")
        return redirect("crear_rack")

    racks_creados = racks.objects.prefetch_related('niveles__secciones').all()
    return render(request, "crearRack.html", {"racks_creados": racks_creados})

# -----------------------------
# EDITAR RACK
# -----------------------------
@csrf_exempt
def editar_rack(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Datos inválidos"})

        rack_id = data.get("id")
        titulo = (data.get("titulo") or "").strip().upper()
        descripcion = (data.get("descripcion") or "").strip().upper()

        if not rack_id or not titulo:
            return JsonResponse({"success": False, "error": "Faltan datos obligatorios"})

        try:
            rack = racks.objects.get(id=rack_id)
            rack.titulo = titulo
            rack.descripcion = descripcion
            rack.save()
            return JsonResponse({"success": True})
        except racks.DoesNotExist:
            return JsonResponse({"success": False, "error": "Rack no encontrado"})
    return JsonResponse({"success": False, "error": "Método no permitido"})

# -----------------------------
# ELIMINAR RACK
# -----------------------------
def eliminar_rack(request):
    if request.method == "POST":
        rack_id = request.POST.get("rack_id")
        if not rack_id:
            messages.error(request, "No se especificó ningún rack.")
            return redirect("crear_rack")

        try:
            rack = racks.objects.get(id=rack_id)
            nombre_rack = rack.titulo  # Guardamos el nombre antes de eliminar
            rack.delete()  # Esto elimina automáticamente niveles y secciones por CASCADE
            messages.success(request, f"Rack '{nombre_rack}' eliminado correctamente junto con sus niveles y secciones.")
            return redirect("crear_rack")
        except racks.DoesNotExist:
            messages.error(request, "Rack no encontrado.")
            return redirect("crear_rack")
    return redirect("crear_rack")













from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import racks, niveles, secciones1, proveedores

# -----------------------------
# CREAR SECCIÓN
# -----------------------------
def crear_seccion(request):
    obtener_racks = racks.objects.filter(estado=True)
    obtener_proveedores = proveedores.objects.all()

    if request.method == "POST":
        rack_id = request.POST.get("pasillo")
        nivel_id = request.POST.get("planta")
        proveedor_id = request.POST.get("proveedor")
        codigos = request.POST.getlist("codigo_seccion[]")

        if not rack_id or not nivel_id:
            messages.error(request, "Debe seleccionar un rack y un nivel.")
            return redirect("crear_seccion")

        nivel_obj = get_object_or_404(niveles, id=nivel_id)
        proveedor_obj = get_object_or_404(proveedores, id=proveedor_id) if proveedor_id else None

        creadas = 0
        repetidas = []

        for codigo in codigos:
            codigo = codigo.strip().upper()
            if not codigo:
                continue
            if secciones1.objects.filter(codigo=codigo).exists():
                repetidas.append(codigo)
                continue
            secciones1.objects.create(
                codigo=codigo,
                descripcion=f"Sección creada manualmente en {nivel_obj.titulo}",
                nivel=nivel_obj,
                proveedor=proveedor_obj,
            )
            creadas += 1

        if creadas:
            messages.success(request, f"{creadas} sección(es) creadas exitosamente.")
        if repetidas:
            messages.warning(request, f"Los siguientes códigos ya existían: {', '.join(repetidas)}")

        return redirect("crear_seccion")

    return render(request, "crearSeccion.html", {
        "obtener_racks": obtener_racks,
        "obtener_proveedores": obtener_proveedores,
        
    })
    

def eliminar_seccion(request):
    if request.method == "POST":
        seccion_id = request.POST.get("id")
        try:
            sec = secciones1.objects.get(id=seccion_id)
            sec.delete()
            return JsonResponse({"status": "ok"})
        except secciones1.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Sección no encontrada"})
    return JsonResponse({"status": "error", "message": "Método no permitido"})


# -----------------------------
# AJAX: Obtener niveles por rack
# -----------------------------
def get_niveles_por_rack(request):
    rack_id = request.GET.get("rack_id")
    niveles_qs = niveles.objects.filter(rack_id=rack_id).values("id", "titulo", "descripcion")
    return JsonResponse(list(niveles_qs), safe=False)


# -----------------------------
# AJAX: Obtener secciones por nivel
# -----------------------------
def get_secciones_por_nivel(request):
    nivel_id = request.GET.get("planta_id")
    secciones_qs = secciones1.objects.filter(nivel_id=nivel_id).values("id", "codigo", "descripcion")
    return JsonResponse(list(secciones_qs), safe=False)

































# -----------------------------
# CREAR NIVEL
# -----------------------------

def crear_nivel(request):
    datos_racks = racks.objects.all()

    if request.method == 'POST':
        codigo = (request.POST.get("codPlanta") or "").strip()
        descripcion = (request.POST.get("descPlanta") or "").strip()
        rack_id = (request.POST.get("lista_estanteria") or "").strip()

        # Validar que todos los campos estén llenos
        if not codigo or not descripcion or not rack_id:
            messages.error(request, "Debe completar todos los campos y seleccionar un rack.")
            return redirect("crear_nivel")

        # Validar que el rack exista
        try:
            rack_obj = racks.objects.get(id=rack_id)
        except racks.DoesNotExist:
            messages.error(request, "El rack seleccionado no existe.")
            return redirect("crear_nivel")

        codigo_normalizado = codigo.upper()

        # Validar duplicado del nivel en cualquier rack o solo en este rack
        if niveles.objects.filter(codigo=codigo_normalizado, rack=rack_obj).exists():
            messages.error(request, f"El nivel '{codigo_normalizado}' ya existe en este rack.")
            return redirect("crear_nivel")

        # Validar número máximo de niveles por rack
        niveles_creados = niveles.objects.filter(rack=rack_obj).count()
        if niveles_creados >= rack_obj.secciones_maximas:
            messages.error(request, f"No se pueden crear más niveles en el rack '{rack_obj.titulo}'.")
            return redirect("crear_nivel")

        numero = niveles_creados + 1

        # Crear el nivel
        niveles.objects.create(
            codigo=codigo_normalizado,
            titulo=str(numero).upper(),
            descripcion=descripcion.upper(),
            rack=rack_obj,
            secciones_maximas=rack_obj.secciones_maximas
        )

        messages.success(request, f"Nivel '{numero}' creado exitosamente en el rack '{rack_obj.titulo}'!")
        return redirect("crear_nivel")

    return render(request, 'crearNivel.html', {"datos_racks": datos_racks})

# -----------------------------
# ENDPOINT PARA OBTENER INFO DEL RACK (JSON)
# -----------------------------
def get_info_rack(request, rack_id):
    try:
        rack_obj = racks.objects.get(id=rack_id)
    except racks.DoesNotExist:
        return JsonResponse({"error": "Rack no encontrado"}, status=404)

    niveles_rack = niveles.objects.filter(rack=rack_obj).order_by('titulo')
    plantas = [{"numero": n.titulo, "descripcion": n.descripcion} for n in niveles_rack]
    plantas_creadas = niveles_rack.count()

    data = {
        "id": rack_obj.id,
        "titulo": rack_obj.titulo,
        "descripcion": rack_obj.descripcion,
        "secciones_maximas": rack_obj.secciones_maximas,
        "plantas_creadas": plantas_creadas,
        "plantas": plantas
    }
    return JsonResponse(data)


# -----------------------------
# AJAX: Información del rack
# -----------------------------
def get_info_rack(request, rack_id):
    rack = racks.objects.get(id=rack_id)
    niveles_queryset = niveles.objects.filter(rack=rack).order_by('id')
    niveles_creados = niveles_queryset.count()
    secciones_maximas = rack.secciones_maximas

    niveles_list = [{"numero": n.titulo, "descripcion": n.descripcion} for n in niveles_queryset]

    return JsonResponse({
        "codigo": rack.codigo,
        "titulo": rack.titulo,
        "descripcion": rack.descripcion,
        "niveles_creados": niveles_creados,
        "secciones_maximas": secciones_maximas,
        "niveles": niveles_list
    })


# -----------------------------
# PROXY PARA OPENROUTER
# -----------------------------
@csrf_exempt
def openrouter_proxy(request):
    """Recibe POST desde el frontend y reenvía la petición a OpenRouter usando
    la clave almacenada en las variables de entorno del servidor.
    """
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        payload = json.loads(request.body)
    except Exception:
        return JsonResponse({"error": "JSON inválido"}, status=400)

    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return JsonResponse({"error": "OPENROUTER_API_KEY no configurada en el servidor"}, status=500)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'X-Forwarded-For': request.META.get('REMOTE_ADDR', ''),
        'X-Title': request.headers.get('X-Title', 'frontend-proxy')
    }

    try:
        resp = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )

        # Reenvía el contenido tal cual y el status code
        content_type = resp.headers.get('Content-Type', 'application/json')
        return HttpResponse(resp.content, status=resp.status_code, content_type=content_type)

    except requests.RequestException as e:
        return JsonResponse({"error": "Error al comunicarse con OpenRouter", "detail": str(e)}, status=502)







# -----------------------------
# CREAR NIVEL
# -----------------------------
@csrf_exempt
def crear_nivel(request):
    datos_racks = racks.objects.all()

    if request.method == 'POST':
        codigo = (request.POST.get("codPlanta") or "").strip()
        descripcion = (request.POST.get("descPlanta") or "").strip()
        rack_id = (request.POST.get("lista_estanteria") or "").strip()

        # Validaciones
        if not codigo or not descripcion or not rack_id:
            return JsonResponse({"success": False, "error": "Debe completar todos los campos y seleccionar un rack."})

        try:
            rack_obj = racks.objects.get(id=rack_id)
        except racks.DoesNotExist:
            return JsonResponse({"success": False, "error": "El rack seleccionado no existe."})

        codigo_normalizado = codigo.upper()

        if niveles.objects.filter(codigo=codigo_normalizado, rack=rack_obj).exists():
            return JsonResponse({"success": False, "error": f"El nivel '{codigo_normalizado}' ya existe en este rack."})

        niveles_creados = niveles.objects.filter(rack=rack_obj).count()
        if niveles_creados >= rack_obj.secciones_maximas:
            return JsonResponse({"success": False, "error": f"No se pueden crear más niveles en el rack '{rack_obj.titulo}'."})

        numero = niveles_creados + 1
        nivel = niveles.objects.create(
            codigo=codigo_normalizado,
            titulo=str(numero).upper(),
            descripcion=descripcion.upper(),
            rack=rack_obj,
            secciones_maximas=rack_obj.secciones_maximas
        )

        # Respuesta para AJAX
        return JsonResponse({
            "success": True,
            "message": f"Nivel '{numero}' creado exitosamente!",
            "nivel_descripcion": nivel.descripcion,
            "nivel": {
                "id": nivel.id,
                "numero": nivel.titulo,
                "descripcion": nivel.descripcion
            }
        })

    # GET request: solo renderizamos el template
    return render(request, 'crearNivel.html', {"datos_racks": datos_racks})

# -----------------------------
# EDITAR NIVEL (AJAX)
# -----------------------------
@csrf_exempt
def editar_nivel(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            nivel_id = data.get("id")
            descripcion = (data.get("descripcion") or "").upper()

            nivel = niveles.objects.get(id=nivel_id)
            nivel.descripcion = descripcion
            nivel.save()
            return JsonResponse({"success": True})
        except niveles.DoesNotExist:
            return JsonResponse({"success": False, "error": "Nivel no encontrado"})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "JSON inválido"})

    return JsonResponse({"success": False, "error": "Método no permitido"})

# -----------------------------
# ELIMINAR NIVEL (AJAX)
# -----------------------------
@csrf_exempt
def eliminar_nivel(request):
    if request.method == "POST":
        nivel_id = request.POST.get("nivel_id")
        try:
            # Obtener el nivel
            nivel = niveles.objects.get(id=nivel_id)

            # Obtener las secciones asociadas (solo para mostrar en la respuesta)
            secciones_list = [
                {"id": s.id, "codigo": s.codigo, "descripcion": s.descripcion}
                for s in nivel.secciones.all()  # <-- corregido
            ]

            # Eliminar el nivel (el CASCADE eliminará las secciones automáticamente)
            nivel.delete()

            # Responder con éxito y las secciones eliminadas
            return JsonResponse({
                "success": True,
                "message": f"Nivel '{nivel.titulo}' eliminado correctamente.",
                "secciones_eliminadas": secciones_list
            })

        except niveles.DoesNotExist:
            return JsonResponse({"success": False, "error": "Nivel no encontrado"})

    return JsonResponse({"success": False, "error": "Método no permitido"})

# -----------------------------
# OBTENER INFO DE RACK (AJAX)
# -----------------------------
def get_info_rack(request, rack_id):
    try:
        rack = racks.objects.get(id=rack_id)
        niveles_rack = niveles.objects.filter(rack=rack).order_by("titulo")
        niveles_list = []

        for n in niveles_rack:
            niveles_list.append({
                "id": n.id,
                "numero": n.titulo,
                "descripcion": n.descripcion,
                "secciones": [{"codigo": s.codigo} for s in n.secciones.all()]  # <-- Aquí
            })

        return JsonResponse({
            "success": True,
            "id": rack.id,
            "titulo": rack.titulo,
            "descripcion": rack.descripcion,
            "niveles": niveles_list,
            "niveles_creados": niveles_rack.count(),
            "secciones_maximas": rack.secciones_maximas
        })
    except racks.DoesNotExist:
        return JsonResponse({"success": False, "error": "Rack no encontrado"}, status=404)





























# -----------------------------
# CREAR UBICACION
# -----------------------------
def crear_ubicacion(request):
    if request.method == "POST":
        codigo = request.POST.get("codigo").strip().upper()
        descripcion_palet = request.POST.get("descripcion").strip().upper()
        rack_id = request.POST.get("pasillo")
        nivel_id = request.POST.get("planta")
        seccion_id = request.POST.get("seccion")
        proveedor_id = request.POST.get("proveedor")
        
        
        print(f"codigo: {codigo}")
        print(f"descripcion_palet: {descripcion_palet}")
        print(f"rack_id: {rack_id}")
        print(f"nivel_id: {nivel_id}")
        print(f"seccion_id: {seccion_id}")
        print(f"proveedor_id: {proveedor_id}")

        # Validaciones básicas

        if not rack_id or not nivel_id or not proveedor_id:
            messages.error(request, "Debes seleccionar Rack, Nivel y Proveedor.")
            return redirect("crear_ubicacion")

        if ubicaciones.objects.filter(codigo=codigo).exists():
            messages.error(request, f"Ya existe una ubicación con el código '{codigo}'.")
            return redirect("crear_ubicacion")

        rack_obj = get_object_or_404(racks, id=rack_id)
        nivel_obj = get_object_or_404(niveles, id=nivel_id)
        proveedor_obj = get_object_or_404(proveedores, id=proveedor_id)

        if seccion_id:
            seccion_obj = get_object_or_404(secciones1, id=seccion_id)
        else:
            secc_count = secciones1.objects.filter(nivel=nivel_obj).count() + 1
            seccion_codigo = f"{nivel_obj.titulo}-S{secc_count}"
            seccion_obj = secciones1.objects.create(
                codigo=seccion_codigo,
                descripcion=f"Sección automática en {nivel_obj.titulo}",
                nivel=nivel_obj,
                disponible=True
            )

        ubicaciones.objects.create(
            codigo=codigo,
            descripcion_palet=descripcion_palet,
            rack=rack_obj,
            nivel=nivel_obj,
            seccion=seccion_obj,
            proveedor=proveedor_obj,
            disponible=False
        )

        messages.success(request, f"Ubicación '{codigo}' creada en rack '{rack_obj.titulo}', nivel '{nivel_obj.titulo}', sección '{seccion_obj.codigo}' (ID:{seccion_obj.id}).")
        return redirect("crear_ubicacion")

    obtener_racks = racks.objects.filter(estado=True)
    obtener_proveedores = proveedores.objects.all()

    return render(request, "crearUbicacion.html", {
        "obtener_racks": obtener_racks,
        "obtener_proveedores": obtener_proveedores
    })


# -----------------------------
# AJAX: Obtener secciones por nivel
# -----------------------------
def get_secciones_por_nivel(request):
    nivel_id = request.GET.get("planta_id")
    secciones_qs = secciones1.objects.filter(nivel_id=nivel_id).values("id", "codigo", "descripcion")
    return JsonResponse(list(secciones_qs), safe=False)


# -----------------------------
# CREAR PROVEEDOR
# -----------------------------
def crear_proveedor(request):
    if request.method == 'POST':
        nombre = request.POST.get("nomproovedor")
        telefono = request.POST.get("telproovedor")
        correo = request.POST.get("corproovedor")
        direccion = request.POST.get("dirproovedor")
        
        print(correo)
        print(direccion)
        print(nombre)
        print(telefono)



        if proveedores.objects.filter(nombre=nombre).exists():
            messages.error(request, f"El proveedor '{nombre}' ya existe.")
            return redirect("crear_proveedor")

        proveedores.objects.create(
            nombre=nombre.upper(),
            telefono=telefono,
            correo=correo,
            direccion=direccion.upper()
        )

        messages.success(request, f"Proveedor '{nombre}' creado exitosamente!")
        return redirect("crear_proveedor")

    return render(request, 'crearProovedor.html')


# -----------------------------
# PANEL DE CONTROL
# -----------------------------
def panel_control(request):
    return render(request, 'panel_control.html')
