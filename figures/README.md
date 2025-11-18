# Figures for Synthesis Paper

This directory contains the figures for the PyTSA synthesis paper.

## Files

### Main Figures (for publication)
- **Figure1_TSA_Concept.png** - High-resolution TSA conceptual framework diagram (300 DPI)
- **Figure1_TSA_Concept.pdf** - Vector version of Figure 1 (for print publication)
- **Figure2_Validation.png** - High-resolution validation results (300 DPI)
- **Figure2_Validation.pdf** - Vector version of Figure 2 (for print publication)

### Generation Scripts
- **create_figure1_tsa_concept.py** - Python script to generate Figure 1
- **create_figure2_validation.py** - Python script to generate Figure 2

## Figure Descriptions

### Figure 1: Trial Sequential Analysis Conceptual Framework
A two-panel figure demonstrating:
- **Panel A**: Conclusive evidence scenario where the Z-curve crosses the efficacy boundary
- **Panel B**: Inconclusive evidence scenario where more information is needed despite p<0.05

### Figure 2: Validation of PyTSA Against Reference Software
A two-panel validation figure showing:
- **Panel A**: Scatter plot with correlation analysis (r=0.9998)
- **Panel B**: Bland-Altman agreement analysis (mean error 0.002%)

## Regenerating Figures

To regenerate the figures:

```bash
cd figures
python create_figure1_tsa_concept.py
python create_figure2_validation.py
```

Requirements:
- matplotlib >= 3.4
- numpy >= 1.20
- scipy >= 1.7
- seaborn >= 0.11

## Notes

- All figures are publication-ready at 300 DPI
- Both PNG (raster) and PDF (vector) formats are provided
- Figures are designed for two-column journal layout
- Color schemes are colorblind-friendly
