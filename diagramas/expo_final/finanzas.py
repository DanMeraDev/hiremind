"""Modelo financiero de HireMind: sueldos, capital inicial, flujo mensual y recuperación (24 meses)."""
SBU = 482                                     # salario básico unificado 2026 (Acuerdo Ministerial, dic. 2025)
COSTO_PERSONA = SBU * (1 + 0.1115) + SBU / 12 * 2   # + IESS patronal 11,15 % + décimo 3.º y 4.º
EQUIPO = 6
SUELDOS = EQUIPO * COSTO_PERSONA / 2          # 6 integrantes a medio tiempo
OTROS = {"Marketing digital": 250, "Dominio, landing y correo": 15, "Contabilidad (RIMPE)": 30, "Internet y telefonía": 35}
FIJO = SUELDOS + sum(OTROS.values())

INVERSION = {"Desarrollo del MVP (480 h × $6, aporte de socios)": 480 * 6,
             "Laptop de pruebas 16 GB": 750,
             "Constitución SAS, firma electrónica y marca": 250}
PILOTOS_MES, MESES_PILOTO, CONVERSION = 10, 3, 0.5
NUEVOS = [0, 0, 0, 4, 5, 6, 7, 8, 8, 9, 9, 10] + [10] * 12
PRECIO_LANZ, PRECIO = 199 + 75, 299 + 75      # meses 4-6 lanzamiento; desde el mes 7 normal
COMISION = 0.06
RENUEVA, PLAN = 0.30, 149                     # 30 % compra Plan Crecimiento en el año 2


def flujo():
    meses, caja, clientes = [], -sum(INVERSION.values()), 0
    capital_trabajo = 0.0
    for m in range(1, 25):
        n = NUEVOS[m - 1] + (int(PILOTOS_MES * MESES_PILOTO * CONVERSION) if m == MESES_PILOTO + 1 else 0)
        ing = n * (PRECIO_LANZ if m <= 6 else PRECIO) * (1 - COMISION)
        if m > 12:
            ing += clientes_a1 * RENUEVA * PLAN / 12
        clientes += n
        if m == 12:
            clientes_a1 = clientes
        caja += ing - FIJO
        capital_trabajo = max(capital_trabajo, -(caja + sum(INVERSION.values())))
        meses.append({"mes": m, "nuevos": n, "ingreso": ing, "egreso": FIJO, "caja": caja})
    return meses, capital_trabajo


MESES, CAP_TRABAJO = flujo()
CAPITAL = sum(INVERSION.values()) + CAP_TRABAJO
PAYBACK = next(x["mes"] for x in MESES if x["caja"] >= 0)
EQUILIBRIO_MES = FIJO / (PRECIO * (1 - COMISION))
CLIENTES_A1 = sum(x["nuevos"] for x in MESES[:12])
CLIENTES_A2 = sum(x["nuevos"] for x in MESES[12:])
MERCADO = 58_400 + 9_700                      # pequeñas + medianas A (INEC, REEM 2023)

if __name__ == "__main__":
    print(f"costo persona {COSTO_PERSONA:.0f} · sueldos {SUELDOS:.0f}/mes · fijo {FIJO:.0f}/mes ({FIJO*12:,.0f}/año)")
    print(f"inversión {sum(INVERSION.values()):,} + capital de trabajo {CAP_TRABAJO:,.0f} = capital inicial {CAPITAL:,.0f}")
    print(f"equilibrio {EQUILIBRIO_MES:.1f} clientes/mes · clientes año1 {CLIENTES_A1} año2 {CLIENTES_A2} "
          f"· {CLIENTES_A1/MERCADO:.2%} del mercado · recupera en mes {PAYBACK}")
    for x in MESES:
        print(x["mes"], x["nuevos"], round(x["ingreso"]), round(x["caja"]))
