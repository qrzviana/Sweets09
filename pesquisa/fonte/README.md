# SODIUM GROTESK v0.1 (fonte própria)

Fonte display da marca, gerada por código em `build.py` (fontTools + skia-pathops). Por ser paramétrica, dá para ajustar peso, largura, raios e ink traps mudando poucos números.

- **SodiumGrotesk-Black (Wide):** para wordmark e campanha.
- **SodiumGroteskCompact-Black (Compact, 80% da largura):** para produto, etiqueta e redes.
- **Glifos (47):** A–Z (as minúsculas são mapeadas para as maiúsculas), 0–9 tabulares, `. , : - — / & ®` e ■.
- **Kerning básico:** AV, AY, LT, PA etc.

## DNA
1. Peso Black, sempre reta.
2. Curvas squircle por fora e contraformas retangulares por dentro.
3. Terminais cortados na horizontal ou na vertical.
4. Ink traps nas junções agudas (A, K, M, N, R, V, W, X, Y).
5. O ponto final é um quadrado do tamanho da haste: o sinal rosa da marca.

## Para regerar
```
python -m venv env && env/bin/pip install fonttools skia-pathops brotli
env/bin/python build.py SodiumGrotesk-Black
WS=0.8 RAD=200 FAM="Sodium Grotesk Compact" env/bin/python build.py SodiumGroteskCompact-Black
```

## Limitações da v0.1
Ainda não tem minúsculas nem acentos (Á, Ç, Ö…), e o espaçamento e o kerning são básicos. Para virar fonte de produção, o próximo passo é a revisão de um type designer: ajuste óptico das curvas, overshoots, hinting e acentos (o mercado é UK/UE).
