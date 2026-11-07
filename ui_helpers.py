"""Elementos visuais compartilhados pelas telas da aplicação."""

from html import escape

import streamlit as st


def legenda(texto, cor="azul"):
    """Exibe uma orientação em negrito, com cor e fundo de alto contraste."""
    if cor not in {"azul", "verde", "amarelo", "vermelho"}:
        cor = "azul"
    st.markdown(
        f'<div class="legenda legenda--{cor}" role="note"><strong>{escape(str(texto))}</strong></div>',
        unsafe_allow_html=True,
    )
