# Nexora 
Sistema de gestión para almacenes

## Configuración del entorno

1. Copia el archivo `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edita el archivo `.env` y configura las siguientes variables:
   - `OPENROUTER_API_KEY`: Tu clave API de OpenRouter
   - `DEEPSEEK_API_KEY`: Tu clave API de Deepseek
   - Otras variables de entorno según sea necesario

## Instalar dependencias
```bash
uv sync
```

## Crear base de datos
```bash
uv run src/manage.py makemigrations
uv run src/manage.py migrate
```

## Correr programa
```bash
uv run src/manage.py runserver
```

## Seguridad
- Nunca compartas tus claves API
- No subas el archivo `.env` al control de versiones
- Usa `.env.example` como plantilla para las variables requeridas
