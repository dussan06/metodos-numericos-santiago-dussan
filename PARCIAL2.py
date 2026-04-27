import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.title("Métodos Numéricos - App Prototipo")

# =========================
# INPUT
# =========================
st.sidebar.header("Entrada de datos")

x_input = st.sidebar.text_input("Valores de x", "0,1,2,3,4,5,6")
y_input = st.sidebar.text_input("Valores de y", "1,2,3,4,5,6,7")

func_str = st.sidebar.text_input("Función f(x) (opcional)", "x**2")
usar_funcion = st.sidebar.checkbox("Usar función")

valor = st.sidebar.number_input("Evaluar en x =", value=2.5)

metodo = st.sidebar.selectbox("Método", [
    "Newton Progresivo",
    "Newton Regresivo",
    "Diferencias Centrales",
    "Lagrange",
    "Mínimos Cuadrados"
])

# =========================
# DATOS
# =========================
x = np.array([float(i) for i in x_input.split(",")])

def evaluar_funcion(func, x_vals):
    y_vals = []
    for val in x_vals:
        try:
            y = eval(func, {"x": val, "np": np})
        except:
            y = np.nan
        y_vals.append(y)
    return np.array(y_vals)

if usar_funcion:
    y = evaluar_funcion(func_str, x)
else:
    y = np.array([float(i) for i in y_input.split(",")])

# validación
if np.any(np.isnan(y)) or np.any(np.isinf(y)):
    st.error("⚠️ Error en la función (ej: división por 0)")
    st.stop()

# grado
max_grado = len(x) - 1
grado = st.sidebar.slider("Grado del polinomio", 1, max_grado, min(2, max_grado))

# =========================
# FUNCIONES
# =========================
def grado1(x,y):
    x0,x1 = x[0],x[1]
    y0,y1 = y[0],y[1]

    m = (y1-y0)/(x1-x0)
    b = y0 - m*x0

    pasos = [
        f"m = ({y1}-{y0})/({x1}-{x0}) = {m}",
        f"b = {y0} - {m}*{x0} = {b}",
        f"P1(x) = {m}x + {b}"
    ]

    return np.poly1d([m,b]), pasos


def tabla_diferencias(x,y):
    n = len(x)
    DD = np.zeros((n,n))
    DD[:,0] = y

    pasos = []
    for i in range(1,n):
        val = (y[i]-y[i-1])/(x[i]-x[i-1])
        pasos.append(f"f[x{i-1},x{i}] = ({y[i]}-{y[i-1]})/({x[i]}-{x[i-1]}) = {val}")

    for k in range(1,n):
        for j in range(k,n):
            DD[j,k] = (DD[j,k-1] - DD[j-1,k-1])/(x[j]-x[j-k])

    return DD, pasos


def newton_poly(DD,x,grado):
    poly = np.poly1d(0)
    pasos = []

    for i in range(grado+1):
        term = np.poly1d(1)
        texto = f"{DD[i,i]}"
        for j in range(i):
            term *= np.poly1d([1,-x[j]])
            texto += f"(x - {x[j]})"
        pasos.append(texto)
        poly += DD[i,i]*term

    return poly, pasos


def lagrange(x,y,grado):
    n = grado+1
    poly = np.poly1d(0)

    pasos = ["L0(x):"]
    for j in range(1,n):
        pasos.append(f"(x - {x[j]})/({x[0]} - {x[j]})")

    for i in range(n):
        L = np.poly1d(1)
        for j in range(n):
            if i != j:
                L *= np.poly1d([1,-x[j]])/(x[i]-x[j])
        poly += y[i]*L

    return poly, pasos


def minimos(x,y,grado):
    poly = np.poly1d(np.polyfit(x,y,grado))
    pasos = [
        "Σx, Σy, Σx², Σxy",
        "Resolución del sistema normal"
    ]
    return poly, pasos


def centrales(x,y,valor):
    h = x[1]-x[0]
    i = len(x)//2

    dy = (y[i+1]-y[i-1])/(2*h)
    s = (valor-x[i])/h

    pasos = [
        f"h = {h}",
        f"dy = ({y[i+1]} - {y[i-1]})/(2*{h}) = {dy}",
        f"s = ({valor}-{x[i]})/{h} = {s}",
        f"P ≈ {y[i]} + s*h*dy"
    ]

    res = y[i] + s*h*dy
    return res, pasos


# =========================
# EJECUCIÓN
# =========================
if st.button("Calcular"):

    DD, _ = tabla_diferencias(x,y)

    resultados = {}

    # calcular todos para comparación
    polyN,_ = newton_poly(DD,x,grado)
    resultados["Newton"] = polyN(valor)

    polyL,_ = lagrange(x,y,grado)
    resultados["Lagrange"] = polyL(valor)

    polyM,_ = minimos(x,y,grado)
    resultados["Mínimos"] = polyM(valor)

    resC,_ = centrales(x,y,valor)
    resultados["Centrales"] = resC

    # =========================
    # MÉTODO SELECCIONADO
    # =========================
    if metodo == "Newton Progresivo":

        _, pasos1 = grado1(x,y)
        st.subheader("Polinomio grado 1")
        for p in pasos1:
            st.write(p)

        DD, pasosDD = tabla_diferencias(x,y)
        st.subheader("Diferencias divididas")
        for p in pasosDD:
            st.write(p)

        poly, pasos = newton_poly(DD,x,grado)
        res = poly(valor)

    elif metodo == "Newton Regresivo":

        _, pasos1 = grado1(x,y)
        st.subheader("Polinomio grado 1")
        for p in pasos1:
            st.write(p)

        DD, pasosDD = tabla_diferencias(x,y)
        st.subheader("Diferencias divididas")
        for p in pasosDD:
            st.write(p)

        poly, pasos = newton_poly(DD,x,grado)
        res = poly(valor)

    elif metodo == "Lagrange":

        _, pasos1 = grado1(x,y)
        st.subheader("Polinomio grado 1")
        for p in pasos1:
            st.write(p)

        poly, pasos = lagrange(x,y,grado)
        res = poly(valor)

    elif metodo == "Mínimos Cuadrados":

        _, pasos1 = grado1(x,y)
        st.subheader("Polinomio grado 1")
        for p in pasos1:
            st.write(p)

        poly, pasos = minimos(x,y,grado)
        res = poly(valor)

    elif metodo == "Diferencias Centrales":

        _, pasos1 = grado1(x,y)
        st.subheader("Polinomio grado 1")
        for p in pasos1:
            st.write(p)

        res, pasos = centrales(x,y,valor)
        poly = polyN

    # =========================
    # RESULTADOS
    # =========================
    st.subheader("Polinomio")
    st.write(poly)

    st.subheader("Resultado")
    st.write(res)

    # gráfica
    xp = np.linspace(min(x), max(x), 200)
    plt.figure()
    plt.scatter(x,y, label="Datos")
    plt.plot(xp, poly(xp), label="Polinomio")
    plt.legend()
    st.pyplot(plt)

    # =========================
    # COMPARACIÓN DE ERROR
    # =========================
    if usar_funcion:
        real = eval(func_str, {"x": valor, "np": np})

        data = []
        for nombre, aprox in resultados.items():
            error = abs(real - aprox)
            error_rel = error/abs(real) if real != 0 else 0
            data.append([nombre, aprox, error, error_rel])

        df = pd.DataFrame(data, columns=["Método","Aprox","Error","Error Relativo"])

        st.subheader("Comparación de errores")
        st.dataframe(df)

        mejor = df.loc[df["Error Relativo"].idxmin()]
        st.success(f"Mejor método: {mejor['Método']}")

    # firma
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center;'>"
        "<b>Diseñado por Santiago Dussan Luna</b><br>"
        "</div>",
        unsafe_allow_html=True
    )