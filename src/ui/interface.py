import streamlit as st
from pathlib import Path

class Interface:

    # === Constructor ===
    def __init__(self, chatbot):
        self.chatbot = chatbot
        self.root =  BASE_DIR = Path(__file__).resolve().parent.parent / "assets" / "images"
        self.me_icon = self.root / "me.png"
        self.bot_icon = self.root / "bot.png"
        self.info_icon = self.root / "info.png"

    
    # === Cargar la página  completa ===
    def render(self):

        # Configuración de la página.
        st.set_page_config(
            page_title="ChatBot recomendador de Portátiles",
            layout="centered"
        )

        # Barra lateral.
        with st.sidebar:

            st.markdown("### Opciones de visualización")

            st.session_state.setdefault("show_urls", False)

            # Mostrar/Ocultar URLs
            if st.session_state["show_urls"]:
                if st.button("❌ Ocultar URLs de compra"):
                    st.session_state["show_urls"] = False
                    st.rerun()
            else:
                if st.button("👁️ Mostrar URLs"):
                    st.session_state["show_urls"] = True
                    st.rerun()

            # Botón borrar conversación
            if st.button("🗑️ Borrar conversación"):
                st.session_state["messages"] = [
                    {"role": "assistant", "content": "Conversación borrada. ¿En qué puedo ayudarte ahora?"}
                ]
                st.rerun()

            st.divider()

            # Información del proyecto
            col_i, col_t = st.columns([1, 12])
            with col_i:
                st.image(self.info_icon, width=22)
            with col_t:
                st.markdown("### Información del proyecto")
                st.write(
                    "Asistente que recomienda ordenadores portátiles según tu uso, presupuesto y preferencias. "
                    "Muestra una lista de ordenadores portátiles junto con sus características principales "
                    "y una breve justificación de cada recomendación."
                )
        
        st.title("💻Recomendador de Portátiles💻")

        if "messages" not in st.session_state: # Verificamos si hay una clave ya creada (si no es que se acaba de iniciar la página)
             st.session_state["messages"] = [
            {"role": "assistant", "content": "Hola, ¿Tienes alguna pregunta?"}
            ]
            # Si la clave no existe, se crea.
            #Cada mensaje contiene:
                #role: quién habla ("assistant" o "user")
                #content: el texto del mensaje


        # Mostrar todos los mensajes guardados
        for msg in st.session_state["messages"]:
            avatar = self.bot_icon if msg["role"] == "assistant" else self.me_icon
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])


        # Almacenamos la pregunta del usuario.
        user_input = st.chat_input("Escribe aquí tu pregunta")

        if user_input:
            # Se guarda el mensaje del Usuario
            st.session_state["messages"].append({"role": "user", "content": user_input})

            # Se muestra el mensaje del Usuario
            with st.chat_message("user", avatar= self.me_icon):
                st.markdown(user_input)

            # Se muestra la respuesta del Chatbot
            with st.chat_message("assistant",avatar=self.bot_icon):
                with st.spinner("Pensando..."):
                    answer = self.chatbot.query(user_input,st.session_state.get("show_urls"))
                    st.markdown(answer)

            # Se guarda la respuesta del Chatbot
            st.session_state["messages"].append({"role": "assistant", "content": answer})


            
