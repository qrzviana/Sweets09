# BRUNNANCE — Tokens

> Valores canônicos (aprovados em 12/11/2026, renomeados após a troca de nome). Lidos pelas skills de design.

## Cor
| Token | Valor | Uso |
|---|---|---|
| `color.base.black` (Brunnance Black) | `#0D0A12` | Fundo principal, peças. Preto com toque de roxo |
| `color.reveal.amethyst` | `#3B1F5C` | Só onde a "luz bate" (gradientes, reflexos) |
| `color.reveal.glint` | `#8C5BD0` | Pontos de brilho; nunca chapado |
| `color.ink.bone` | `#ECE8E1` | Texto principal e logo sobre escuro |
| `color.ink.smoke` | `#8E8796` | Texto secundário, legendas |
| `color.signal.pink` | `#FF2E7E` | O sinal (quadrado/ponto final). No máximo 1% |
| `color.base.deep` | `#08060B` | Fundo mais profundo, vinhetas |

Contraste: bone sobre black ≈ 16:1; smoke sobre black ≈ 5,9:1 (passa AA); pink sobre black ≈ 5,6:1 (passa AA).

## Tipografia
| Token | Valor |
|---|---|
| `font.display` | Fonte própria (v0.1, Black, em revisão): `pesquisa/fonte/SodiumGrotesk-Black.otf` (Wide) e `SodiumGroteskCompact-Black.otf` (Compact). O nome do arquivo é anterior à troca de nome |
| `font.text` | Neutra, licenciada, a definir (provisória: Archivo) |
| `font.display.tracking` | 0 a −1% no display; +6 a +8% nos rótulos em caixa-alta |
| `font.display.case` | Sempre caixa-alta no display |

## Forma e sinal
| Token | Valor |
|---|---|
| `signal.size` | Quadrado do tamanho da haste vertical da letra (≈ 0,2 em) |
| `signal.position` | Na linha de base, depois da última letra, como ponto final |
| `radius.ui` | 0 (cantos vivos) |

## Imagem
| Token | Valor |
|---|---|
| `image.light` | Flash direto ou luz de rua, sempre depois do pôr do sol |
| `image.grain` | Grão de filme visível (ruído 15–22%) |
| `image.reveal` | Gradiente radial ametista partindo de uma fonte de luz |
