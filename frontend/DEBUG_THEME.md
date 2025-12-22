# Debug Dark Mode

## Pasos para depurar:

1. Abre el navegador y abre la consola de desarrollador (F12)

2. Verifica el localStorage:
```javascript
// En la consola del navegador:
localStorage.getItem('agentlab-theme-storage')
```

3. Si ves un valor, debería ser algo como:
```json
{"state":{"theme":"light","preferences":{...}},"version":0}
```

4. Para limpiar el localStorage y empezar de nuevo:
```javascript
// En la consola del navegador:
localStorage.removeItem('agentlab-theme-storage')
// Luego recarga la página
location.reload()
```

5. Verifica la clase en el elemento HTML:
```javascript
// En la consola del navegador:
document.documentElement.classList.contains('dark')
// Debería retornar true si está en dark mode, false si está en light
```

6. Prueba cambiar el tema manualmente:
```javascript
// En la consola del navegador:
document.documentElement.classList.remove('dark')  // Para light
document.documentElement.classList.add('dark')     // Para dark
```

7. Mira los logs en la consola cuando cambies el tema en Settings.
   Deberías ver:
   - "Setting theme to: light" o "Setting theme to: dark"
   - "Adding dark class" o "Removing dark class"
   - "App useEffect - current theme: light" o "dark"

## Solución si no funciona:

Si el problema persiste, ejecuta esto en la consola:
```javascript
localStorage.clear()
location.reload()
```

Esto limpiará todo el localStorage y la app empezará en light mode por defecto.
