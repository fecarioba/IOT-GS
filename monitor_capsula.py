import cv2
import numpy as np

# Dados simulados
temperatura = 25
luminosidade = 700

while True:

    # Cria uma tela preta
    tela = np.zeros((600, 900, 3), dtype=np.uint8)

    # Título
    cv2.putText(
        tela,
        "MONITORAMENTO DA CAPSULA ESPACIAL",
        (150, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    # Define status da cápsula
    if temperatura <= 30:
        status = "NORMAL"
        cor = (0, 255, 0)      # Verde

    elif temperatura <= 40:
        status = "ALERTA"
        cor = (0, 255, 255)    # Amarelo

    else:
        status = "CRITICO"
        cor = (0, 0, 255)      # Vermelho

    # Desenha uma cápsula simples
    cv2.rectangle(tela, (50, 100), (350, 500), (255, 255, 255), 2)

    cv2.putText(
        tela,
        "CAPSULA",
        (130, 300),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )

    # Indicador de status
    cv2.circle(tela, (250, 150), 25, cor, -1)

    # Informações
    cv2.putText(
        tela,
        f"Temperatura: {temperatura} C",
        (450, 180),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.putText(
        tela,
        f"Luminosidade: {luminosidade}",
        (450, 260),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.putText(
        tela,
        f"STATUS: {status}",
        (450, 340),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        cor,
        3
    )

    cv2.imshow("Capsula Espacial", tela)

    tecla = cv2.waitKey(100)

    if tecla == 27:  # ESC
        break

cv2.destroyAllWindows()