import streamlit as st
import mysql.connector

st.set_page_config(
    page_title="Reservas de Laboratório",
    page_icon="🧪",
    layout="wide"
)

try:
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="reserva"
    )

except mysql.connector.Error as erro:
    st.error(f"Erro ao conectar ao banco de dados: {erro}")
    st.stop()


if "tela" not in st.session_state:
    st.session_state.tela = "menu"


def voltar_menu():
    st.session_state.tela = "menu"
    st.rerun()


if st.session_state.tela == "menu":

    st.title("🧪 Sistema de Reservas de Laboratório")

    st.write(
        "Bem-vindo ao sistema de gerenciamento "
        "de reservas dos laboratórios."
    )

    st.divider()

    st.subheader("Menu principal")

    st.write("Selecione uma opção:")

    coluna1, coluna2 = st.columns(2)

    with coluna1:
        if st.button(
            "📅 Nova Reserva",
            use_container_width=True
        ):
            st.session_state.tela = "nova_reserva"
            st.rerun()

    with coluna2:
        if st.button(
            "📋 Consultar Reservas",
            use_container_width=True
        ):
            st.session_state.tela = "consultar_reservas"
            st.rerun()


elif st.session_state.tela == "nova_reserva":

    st.title("📅 Nova Reserva")

    st.write(
        "Preencha os dados para realizar uma reserva."
    )

    st.divider()

    nome_professor = st.text_input(
        "Nome do professor",
        placeholder="Digite o nome do professor"
    )

    laboratorio = st.selectbox(
        "Laboratório",
        [
            "Laboratório de Informática 1",
            "Laboratório de Informática 2",
            "Laboratório de Química",
            "Laboratório de Física"
        ]
    )

    data_reserva = st.date_input(
        "Data da reserva"
    )

    st.subheader("⏄1�7 Horário da reserva")

    st.write(
        "Escolha o horário de início e o horário de término."
    )

    horarios = [
        "13:00",
        "13:50",
        "14:40",
        "15:30",
        "15:45",
        "16:35",
        "17:25",
        "18:15"
    ]

    coluna1, coluna2 = st.columns(2)

    with coluna1:
        hora_inicio = st.selectbox(
            "Horário de início",
            horarios
        )

    with coluna2:
        horarios_disponiveis = [
            horario
            for horario in horarios
            if horario > hora_inicio
        ]

        hora_termino = st.selectbox(
            "Horário de término",
            horarios_disponiveis
        )

    st.info(
        f"Horário selecionado: "
        f"**{hora_inicio} - {hora_termino}**"
    )

    st.divider()

    if st.button(
        "✄1�7 Reservar horário",
        use_container_width=True
    ):

        if nome_professor.strip() == "":
            st.error("Digite o nome do professor.")

        else:
            cursor = conexao.cursor()

            cursor.execute(
                """
                SELECT ID
                FROM Laboratorios
                WHERE Nome = %s
                """,
                (laboratorio,)
            )

            resultado = cursor.fetchone()

            if resultado is None:
                st.error("Laboratório não encontrado.")

            else:
                lab_id = resultado[0]

                cursor.execute(
                    """
                    SELECT ID
                    FROM Reservas
                    WHERE Lab_ID = %s
                    AND Data = %s
                    AND Hora_Inicio < %s
                    AND Hora_Fim > %s
                    """,
                    (
                        lab_id,
                        data_reserva,
                        hora_termino,
                        hora_inicio
                    )
                )

                conflito = cursor.fetchone()

                if conflito is not None:
                    st.error(
                        "Este laboratório já está reservado "
                        "nesse horário."
                    )

                else:
                    cursor.execute(
                        """
                        INSERT INTO Reservas (
                            Lab_ID,
                            Nome_Professor,
                            Data,
                            Hora_Inicio,
                            Hora_Fim
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            lab_id,
                            nome_professor,
                            data_reserva,
                            hora_inicio,
                            hora_termino
                        )
                    )

                    conexao.commit()

                    st.success(
                        "Reserva realizada com sucesso!"
                    )

                    st.write(
                        f"**Professor:** {nome_professor}"
                    )

                    st.write(
                        f"**Laboratório:** {laboratorio}"
                    )

                    st.write(
                        f"**Data:** {data_reserva}"
                    )

                    st.write(
                        f"**Horário:** "
                        f"{hora_inicio} - {hora_termino}"
                    )

            cursor.close()

    st.write("")

    if st.button(
        "❄1�7 Fechar",
        use_container_width=True
    ):
        voltar_menu()


elif st.session_state.tela == "consultar_reservas":

    st.title("📋 Consultar Reservas")

    st.write(
        "Aqui estão as reservas cadastradas."
    )

    st.divider()

    cursor = conexao.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT
            Reservas.ID,
            Laboratorios.Nome AS Laboratorio,
            Reservas.Nome_Professor,
            Reservas.Data,
            Reservas.Hora_Inicio,
            Reservas.Hora_Fim,
            Reservas.Data_Criacao
        FROM Reservas
        INNER JOIN Laboratorios
            ON Reservas.Lab_ID = Laboratorios.ID
        ORDER BY Reservas.Data, Reservas.Hora_Inicio
        """
    )

    reservas = cursor.fetchall()

    cursor.close()

    if len(reservas) == 0:

        st.info(
            "Ainda não existem reservas cadastradas."
        )

    else:

        for reserva in reservas:

            st.write(
                f"**ID da reserva:** {reserva['ID']}"
            )

            st.write(
                f"**Professor:** "
                f"{reserva['Nome_Professor']}"
            )

            st.write(
                f"**Laboratório:** "
                f"{reserva['Laboratorio']}"
            )

            st.write(
                f"**Data:** {reserva['Data']}"
            )

            st.write(
                f"**Horário:** "
                f"{reserva['Hora_Inicio']} - "
                f"{reserva['Hora_Fim']}"
            )

            st.write(
                f"**Reserva criada em:** "
                f"{reserva['Data_Criacao']}"
            )

            st.divider()

    if st.button(
        "Voltar ao menu",
        use_container_width=True
    ):
        voltar_menu()