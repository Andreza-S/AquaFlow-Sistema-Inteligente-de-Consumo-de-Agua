# 💧 AquaFlow – Sistema Inteligente de Monitoramento e Previsão de Consumo de Água

### Instituto Federal de Educação, Ciência e Tecnologia da Paraíba (IFPB)  
**Campus:** Campina Grande  
**Curso:** Engenharia da Computação  
**Turma:** 2025.2  
**Componente Curricular:** Técnicas de Prototipagem  
**Docente:** Moacy Pereira da Silva  

---

## 👩‍💻 Equipe de Desenvolvimento
- **Andreza Costa dos Santos**
- **Geovana Stefani Lopes Bezerra**
- **Nivaldo Pereira da Silva Neto**
- **Vinícius Cavalcante Barbosa**


📍 *Campina Grande - PB | 2025*

---

## 🧭 1. Descrição Geral do Projeto

O **AquaFlow** é um sistema inteligente de **monitoramento e previsão de consumo de água** com foco em **sustentabilidade e uso racional dos recursos hídricos**.  

O projeto consiste em um **protótipo funcional (prova de conceito)** capaz de medir, em tempo real, a vazão de água em diferentes pontos de uma instalação hidráulica, registrando o volume consumido e comparando-o com a quantidade total de entrada de água.

Além de detectar **vazamentos e desperdícios**, o sistema utiliza **técnicas de aprendizado de máquina (Machine Learning)** para realizar **previsões de consumo futuro**, oferecendo ao usuário informações para tomada de decisão consciente.  

O AquaFlow integra eletrônica embarcada, ciência de dados e sustentabilidade — pilares das **casas inteligentes** e **cidades inteligentes**.

---

## 🌱 2. Justificativa

O desperdício de água é um dos principais desafios ambientais e econômicos atuais.  
Grande parte das perdas vem de **vazamentos não detectados** e **consumo descontrolado**.  

O **AquaFlow** busca preencher essa lacuna com uma solução:
- 💧 De **baixo custo** e **fácil implementação**  
- 📊 Capaz de registrar **dados em tempo real**  
- ⚙️ Que apoia o **uso consciente da água** e a **gestão eficiente de recursos**

---

## 🌍 3. Impacto e Visão de Futuro

O projeto está alinhado às diretrizes de **Cidades Inteligentes**, promovendo o uso de sensores e dados para a sustentabilidade urbana.  

Em médio e longo prazo, o **AquaFlow** pode ser expandido para:
- Aplicações em residências e pequenas empresas  
- Integração com plataformas urbanas de monitoramento ambiental  
- Apoio técnico à detecção de vazamentos e gestão de consumo  

> 🔹 *O AquaFlow representa a convergência entre engenharia, ciência de dados e sustentabilidade.*

---

## 🎯 4. Objetivo Geral

> **Desenvolver um protótipo funcional de sistema inteligente de monitoramento e previsão de consumo de água**, utilizando sensores de vazão e uma placa **ESP32**, com interface de visualização e análise preditiva.

---

## 🧩 5. Objetivos Específicos

- Implementar leitura contínua de sensores de vazão em diferentes pontos.  
- Criar interface de monitoramento em tempo real (via serial, display ou dashboard).  
- Registrar e analisar o volume de água consumido.  
- Comparar entrada e saída de água, detectando possíveis vazamentos.  
- Implementar modelo preditivo simples (regressão linear ou média móvel).  

---

## ⚙️ 6. Requisitos Funcionais

| Código | Requisito | Descrição |
|:------:|:-----------|:-----------|
| RF01 | Leitura de sensores | Captura contínua da vazão de cada ramal e entrada principal. |
| RF02 | Cálculo de volume | Converte vazão em volume acumulado e registra consumo total. |
| RF03 | Comparação de entrada e saída | Detecta diferenças e possíveis vazamentos. |
| RF04 | Registro de dados | Armazena leituras periódicas em tempo real. |
| RF05 | Exibição das informações | Mostra dados via display local ou dashboard. |
| RF06 | Alertas de anomalia | Emite avisos de consumo irregular. |
| RF07 | Análise preditiva | Estima consumo futuro baseado em dados coletados. |
| RF08 | Recomendações | Gera mensagens sobre uso racional da água. |
| RF09 | Reset de dados | Permite reinicialização do ciclo de medição. |

---

## 🧠 7. Requisitos Não Funcionais

| Código | Requisito | Descrição |
|:------:|:-----------|:-----------|
| RNF01 | Precisão | ±5% nas medições de vazão e volume. |
| RNF02 | Tempo de resposta | Atualizações a cada <2 segundos. |
| RNF03 | Confiabilidade | Operação contínua por 24h sem falhas. |
| RNF04 | Usabilidade | Interface simples e legível para qualquer usuário. |
| RNF05 | Eficiência energética | Consumo inferior a 5 W. |
| RNF06 | Modularidade | Permite substituição de sensores. |
| RNF07 | Manutenibilidade | Código documentado e estruturado. |
| RNF08 | Escalabilidade | Suporte a múltiplos sensores em futuras versões. |

---

## 🔍 8. Escopo

### Escopo Positivo ✅
- Montagem de protótipo com ESP32 e sensores de vazão  
- Medição e registro em tempo real  
- Geração de alertas básicos  
- Implementação de modelo preditivo simples  
- Dashboard ou display de exibição  

### Escopo Negativo ❌
- Aplicativo mobile próprio  
- Integração com concessionárias de água  
- Controle físico automatizado de válvulas  
- Envio de dados para nuvem IoT  
- Escalabilidade em larga escala  

---

## 🧱 9. Planejamento de Atividades

### 📘 **Versão 1 — Prova de Conceito**
| Etapa | Descrição | Responsáveis | Resultado |
|:------|:-----------|:--------------|:-----------|
| 1 | Definição técnica e aquisição de sensores | Todos | Lista de componentes |
| 2 | Montagem do protótipo físico | Todos | Estrutura funcional |
| 3 | Programação (C/Arduino) | Geovana e Vinícius | Leitura e registro de dados |
| 4 | Criação do Dashboard | Geovana | Visualização dos dados |

### 📗 **Versão 2 — Expansão e Preditivo**
| Etapa | Descrição | Responsáveis | Resultado |
|:------|:-----------|:--------------|:-----------|
| 1 | Modelo preditivo (ML) | A | Previsão de consumo |
| 2 | Ampliação física | B + C | Estrutura ampliada |
| 3 | Integração de novos sensores | B + D | Dados adicionais integrados |
| 4 | Refinamento preditivo | B + D | Modelo aprimorado |
| 5 | Dashboard avançado | Todos | Relatórios e alertas gráficos |
| 6 | Documentação final | Todos | Relatório técnico completo |

---

## ⏱️ 10. Cronograma Simplificado

| Data | Etapa |
|:------|:------|
| 02/09 – 03/09 | Definição e aquisição de sensores |
| 17/09 – 10/10 | Montagem e testes elétricos |
| 14/10 – 27/10 | Programação e dashboard |
| 29/10 | Entrega da prova de conceito |
| 04/11 – 26/11 | Implementação e refinamento preditivo |
| 02/12 – 09/12 | Documentação e entrega final |

---

## 🧰 11. Lista de Materiais (BoM)

| Item | Qtde | Descrição |
|:------|:----:|:-----------|
| ESP32 | 1 | Microcontrolador com Wi-Fi e Bluetooth |
| Sensor de Vazão YF-S201 | 4 | Medição da vazão (3 ramais + 1 entrada) |
| Conectores e abraçadeiras | — | Fixação e interconexão hidráulica |
| Protoboard e jumpers | 1 kit | Montagem elétrica |
| Resistores 2k2Ω / 1k2Ω | 4 kits | Ajuste de sinal |
| Fonte 5V 2A | 1 | Alimentação |
| Display LCD 16x2 (opcional) | 1 | Exibição local |

---

## 💬 12. Considerações Finais

O **AquaFlow** demonstra como a **engenharia eletrônica**, a **programação embarcada** e a **análise de dados** podem unir-se em prol da **sustentabilidade ambiental**.  

> 🌎 *Uma gota de inovação pode mudar o futuro da água.*
