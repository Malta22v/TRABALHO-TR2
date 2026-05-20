# Projeto Final TR2 — Adaptive Bitrate Streaming (ABR)

Projeto da disciplina Teleinformática e Redes 2 (TR2).

Implementação de um cliente de streaming adaptativo (ABR) em Python com:

- Download de segmentos HTTP
- Medição de throughput
- Geração de métricas CSV
- Buffer manager
- Políticas ABR
- Failover entre servidores
- Análise com Wireshark

---

# Estrutura do Projeto

```text
tr2-abr-client/
│
├── main.py
├── manifest.py
├── downloader.py
├── metrics.py
├── plot.py
├── requirements.txt
│
├── logs/
│   └── metrics.csv
│
├── graphs/
│   └── throughput.png
│
└── captures/
```

---

# Ambiente Virtual (WSL/Linux)

Criar ambiente virtual:

```bash
python3 -m venv venv
```

Ativar ambiente virtual:

```bash
source venv/bin/activate
```

---

# Instalar Dependências

```bash
pip install -r requirements.txt
```

Caso o requirements.txt não exista:

```bash
pip install requests pandas matplotlib
```

---

# Como Rodar

```bash
python main.py
```

---

# O que o Cliente Faz Atualmente

- Baixa o manifest do servidor
- Faz parsing do JSON
- Baixa segmentos de diferentes qualidades
- Mede:
  - bytes recebidos
  - tempo de download
  - throughput
- Gera CSV automaticamente
- Gera gráfico de throughput
- Compatível com análise no Wireshark

---

# Servidores

Servidor principal:

http://137.131.178.229:8080

Servidor fallback:

http://137.131.178.229:8081

Manifest:

http://137.131.178.229:8080/manifest

---

# CSV Gerado

Arquivo:

```text
logs/metrics.csv
```

Campos atuais:

- segment
- quality
- bytes_received
- download_time_s
- throughput_kbps

---

# Gráfico Gerado

Arquivo:

```text
graphs/throughput.png
```

---

# Wireshark

Filtro recomendado:

```text
tcp.port == 8080
```

---

# Próximos Passos

## Política ABR (Baseline)

Implementar:
- throughput médio
- fator de segurança
- seleção automática de qualidade

---

## Buffer Manager

Implementar:
- buffer_level_s
- buffer_can_play
- rebuffer_event

---

## Failover

Implementar:
- troca automática para servidor B
- health check
- registro no CSV

---

# Observações

O matplotlib está configurado para funcionar no WSL sem interface gráfica usando backend Agg.

---

# Integrantes

- Nome 1
- Nome 2
- Nome 3