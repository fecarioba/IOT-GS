# 🛸 Monitor de Cápsula Espacial — IOT Global Solution 2026.1

Sistema de monitoramento em tempo real para cápsulas espaciais, desenvolvido com **Python + OpenCV + MQTT**, integrando dados de sensores físicos (ESP32 + DHT + LDR) com visão computacional simulada e dashboard via Node-RED.

---

## 📋 Sobre o Projeto

Este projeto foi desenvolvido como Global Solution da disciplina de **Engenharia de Software — IoT** (FIAP, 2026.1). O objetivo é simular o monitoramento interno de uma cápsula espacial, coletando dados de temperatura e luminosidade via ESP32 e exibindo-os em tempo real por meio de uma interface visual construída com OpenCV e um dashboard no Node-RED.

---

## 🧰 Tecnologias Utilizadas

| Tecnologia | Função |
|---|---|
| Python 3 | Lógica principal e visão computacional |
| OpenCV | Renderização da interface visual |
| MQTT (HiveMQ) | Comunicação entre ESP32 e Python/Node-RED |
| Node-RED | Dashboard com gauges e gráficos |
| ESP32 | Microcontrolador com DHT (temperatura) e LDR (luminosidade) |

---

## 📁 Estrutura do Repositório

```
IOT-GS/
├── monitor_capsula.py   # Aplicação principal de visão computacional
├── capsula.webp         # Imagem da cápsula espacial usada na interface
└── README.md
```

---

## ▶️ Como Executar

### Pré-requisitos

```bash
pip install opencv-python numpy paho-mqtt
```

### Rodando o monitor

```bash
python monitor_capsula.py
```

Por padrão o sistema conecta ao broker público HiveMQ e aguarda dados nos tópicos `capsula/temperatura` e `capsula/luminosidade`.

Para testar **sem hardware**, altere a variável no início do arquivo:

```python
modo_simulacao = True
```

Em modo simulação, use as teclas:

| Tecla | Ação |
|---|---|
| `Q` / `A` | Temperatura + / − |
| `W` / `S` | Luminosidade + / − |
| `ESC` | Encerra o programa |

---

## 📡 Tópicos MQTT

| Tópico | Tipo | Descrição |
|---|---|---|
| `capsula/temperatura` | float | Temperatura interna em °C |
| `capsula/luminosidade` | int | Luminosidade em % (0–100) |

Broker: `broker.hivemq.com` — porta `1883`

---

## 🚦 Lógica de Status

| Condição | Status | Cor |
|---|---|---|
| 20°C ≤ temp ≤ 30°C e lux ≥ 15% | NORMAL | 🟢 Verde |
| temp < 20°C ou temp > 30°C ou lux < 15% | ALERTA | 🟡 Amarelo |
| temp < 10°C ou temp > 40°C | CRITICO | 🔴 Vermelho |

---

## 👥 Integrantes

Djalma Moreira de Andrade Filho - RM555530

Felipe Paes de Barros Muller Carioba - RM558447

Lucas Rodrigues de Queiroz - RM556323

Matheus Gushi Morioka - RM556935

Victor Hugo de Paula - RM554787
