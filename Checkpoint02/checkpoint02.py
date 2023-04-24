import cv2
import numpy as np

video = cv2.VideoCapture('pedra-papel-tesoura.mp4')

ret, frame = video.read()

#intervalo
pedra_area = (15800.0, 17000.0)
papel_area = (19350.0, 19500.0)
tesoura_area = (15250.0, 15500.0)

pontos_jogador1 = 0
pontos_jogador2 = 0
contador_frames1 = 0
contador_frames2 = 0


while True:
    ret, frame = video.read()
    frame = cv2.resize(frame, (1000, 600))
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 200, 400)

    #segmentação de cores para criar a mascara
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 200], dtype=np.uint8)
    upper = np.array([255, 30, 255], dtype=np.uint8)
    mascara = cv2.inRange(hsv, lower, upper)

    #inverte a mascara para obter os objetos diferentes da cor branca
    mascara_inv = cv2.bitwise_not(mascara)

    #aplica um filtro de desfoque gaussiano na imagem
    blurred = cv2.GaussianBlur(mascara_inv, (5, 5), 0)

    contours, hierarchy = cv2.findContours(
        blurred, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Ordenar os contornos por área em ordem decrescente
    contours = sorted(contours, key=cv2.contourArea, reverse=True) 

    # Divide o frame em duas metades
    altura, largura, _ = frame.shape
    lado_jogador1 = frame[:, :largura // 2, :]
    lado_jogador2 = frame[:, largura // 2:, :]

   # Obter as jogadas dos jogadores
    if len(contours) >= 2:
        jogada_jogador1 = None
        jogada_jogador2 = None
        # Itera pelos dois maiores contornos encontrados, ordenados por área de forma decrescente.
        for i, contour in enumerate(sorted(contours, key=cv2.contourArea, reverse=True)[:2]): 
            #Obtém a área e as coordenadas do retângulo
            area = cv2.contourArea(contour)
            x, y, w, h = cv2.boundingRect(contour)
            
            # Determina se o contorno representa uma jogada de pedra, papel ou tesoura
            if pedra_area[0] <= area <= pedra_area[1]:
                jogada = "pedra"
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
                cv2.putText(frame, "Pedra", (x, y - 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
            elif papel_area[0] <= area <= papel_area[1]:
                jogada = "papel"
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
                cv2.putText(frame, "Papel", (x, y - 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            elif tesoura_area[0] <= area <= tesoura_area[1]:
                jogada = "tesoura"
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
                cv2.putText(frame, "Tesoura", (x, y - 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            #Atribui a jogada ao jogador correspondente.   
            # se a coordenada x do primeiro ponto do contorno estiver mais à esquerda, a jogada é atribuida ao jogador 1. 
            # se estiver à direita, é do jogador 2        
            if contour[0][0][0] < largura // 2:
                jogada_jogador1 = jogada
            else:
                jogada_jogador2 = jogada

        # Verificar quem ganhou a rodada e atualizar os pontos
        if jogada_jogador1 == "pedra" and jogada_jogador2 == "tesoura":
            cv2.putText(frame, "Jogador 1 ganhou", (200, 50),
                        cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 255), 2)
            contador_frames1 += 1
               
        if jogada_jogador1 == "tesoura" and jogada_jogador2 == "papel":
            cv2.putText(frame, "Jogador 1 ganhou", (200, 50),
                        cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 255), 2)
            contador_frames1 += 1
             #contabilizar pontos a cada 90 frames 
            if contador_frames1 == 90:
                pontos_jogador1 += 1
                contador_frames1 = 0  
                
        elif jogada_jogador1 == "papel" and jogada_jogador2 == "pedra":
            cv2.putText(frame, "Jogador 1 ganhou", (200, 50),
                        cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 255), 2)
            contador_frames1 += 1
            if contador_frames1 == 90:
                pontos_jogador1 += 1
                contador_frames1 = 0  
                
        elif jogada_jogador1 == jogada_jogador2:
            cv2.putText(frame, "Empate", (400, 50),
                        cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 2)
            pass

        else:
            cv2.putText(frame, "Jogador 2 ganhou", (400, 50),
                        cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 2)
            contador_frames2 += 1
            if contador_frames2 == 90:
                pontos_jogador2 += 1
                contador_frames2 = 0 
                
    # # Exibir os pontos na tela
    cv2.putText(frame, "Placar:", (
        30, 100), cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(frame, f"Jogador 1: {pontos_jogador1}", (
        5, 150), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 0, 255), 2)
    cv2.putText(frame, f"Jogador 2: {pontos_jogador2}", (
        5, 200), cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 0, 0), 2)

    frame = np.concatenate((lado_jogador1, lado_jogador2), axis=1)

    cv2.imshow('Jogo jokenpo', frame)

    if cv2.waitKey(1) & 0xFF == ord('x'):
        break

video.release()
cv2.destroyAllWindows()