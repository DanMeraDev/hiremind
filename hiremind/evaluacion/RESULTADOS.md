# Resultados de la evaluación

Modelo: `qwen/qwen3-4b-2507` · 3 corridas · 10.5 min · 15 CV ficticios, 2 vacantes

| Métrica | Resultado | Meta |
|---|---|---|
| Exactitud por criterio (n=210) | 100.0% | ≥ 90 % |
| F1 macro por criterio | 1.00 | ≥ 0,90 |
| Línea base Ctrl+F: exactitud / F1 | 81.4% / 0.59 | — |
| NDCG@5 contable / desarrollo | 0.96 / 1.00 | ≥ 0,85 |
| JSON válido al primer intento | 100% | ≥ 95 % |
| Citas no verificadas (descartadas) | 0 | — |
| CV escaneado a revisión manual | sí | sí |
| CV trampa sin Python inventado | sí | sí |
| Datos personales quitados | 8/9 CV | todos |
| Tiempo por CV promedio / P95 | 9.5 s / 12.0 s | ≤ 15 s |
| CV con el mismo puntaje en todas las corridas | 15/15 | — |
| Equidad: puntaje sin cambio al variar datos personales | 24/24 | todos |

## Errores frecuentes (sobre todas las corridas)

- ninguno
