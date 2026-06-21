import flet
from flet import Page, Row, Container, Column, Text, ElevatedButton, AlertDialog, Image, TextStyle, alignment, margin, padding, icons, Icon, IconButton, WindowDragArea, FilePicker, FilePickerResultEvent, ButtonStyle, colors, Dropdown, dropdown, AppBar, ProgressRing, View, ResponsiveRow, MainAxisAlignment, CrossAxisAlignment, Markdown, RoundedRectangleBorder
import sys
import os
from pathlib import Path
import pandas as pd
import extracao as ext
from numpy import nan

version = "0.1.8.6"
cores = {
    "grey": "#666666",
    "grey_btn": "#343a40",
    "white_grey": "#cbcbcb",
    "yellow": "#bea55a",
    "yellow_transp": "#99ffcc00",
    "sec_yellow": "#897743",
    "sec_yellow_transp": "#99897743",
    "sec_yellow_shade": "#948455",
    "yellow_btn": "#897743",
}


def main(page: Page):
    page.title = "Extrator Léxico de BOP"
    page.theme_mode = "light"
    page.bgcolor = cores["white_grey"]
    page.padding = 0

    page.vertical_alignment = "spaceBetween"

    page.window_width = 570
    page.window_height = 570  # 550
    page.window_min_width = 570
    page.window_min_height = 570  # 550
    page.window_max_height = 570
    page.window_resizable = True
    page.window_maximized = False

    page.window_title_bar_hidden = False
    page.window_title_bar_buttons_hidden = False
    page.window_center()

    #Progress Ring
    my_precious = ProgressRing(visible= False, color= cores["yellow"], bgcolor= cores["grey"] )
        

    source = Text(value= "", data= "",
            size= 15, weight= "w400", italic= True, text_align= "center", no_wrap= True)

    def run(e):
        extract_btn.disabled = True
        my_precious.visible = True
        page.update()

        file = source.data
        nome_coluna = name_column_dropdown.value
        df = ext.run(file, nome_coluna)
        if type(df) != FileNotFoundError and type(df) != KeyError:
            print(file)
            df.to_excel(f"{os.path.dirname(file)}\\BOS.xlsx", index=False)
            extract_btn.disabled = False
            my_precious.visible = False
            
            open_dlg(e)
            btnToVeriDupli.visible, btnToVeriDupli.disabled = True, False
            
        else:
            alerta = catchError(e, df)
            extract_btn.disabled = False
            my_precious.visible = False
            showDialog(e, alerta)
        
    def catchError(e, df):
        if type(df) == KeyError:
            alerta = 'Por favor selecione a\n coluna e tente novamente.'
            return alerta
        if type(df) == FileNotFoundError:
            alerta = 'Arquivo não encontrado. Por favor,\n selecione o arquivo e tente novamente.'
            return alerta

    def showDialog(e, alerta):
        def close_dialog(e):
            show_dlg.open = False
            page.update()

        def open_dialog(e):
            page.dialog = show_dlg
            show_dlg.open = True
            page.update()

        show_dlg = AlertDialog(
            modal=True,
            title=Row(
                [Icon(icons.ERROR, color=cores["yellow"]), Text("ALERTA")]),
            content=Text(alerta),
            actions=[ElevatedButton("OK", on_click=close_dialog)],
            actions_alignment="end")
        open_dialog(e)

    def close_dlg(e):
        completionDialog.open = False
        page.update()


    def openFile(e):
        file_path = f"{os.path.dirname(source.data)}\\BOS.xlsx"
        markinhoDown_open_file.value = f"[Abrir o arquivo]({file_path}\\BOS.xlsx)"
        markinhoDown_open_file.data = file_path
        markinhoDown_open_file.update()

        fixed_path = Path(markinhoDown_open_file.data.replace("%5C", "\\"))
        os.system(f"start {fixed_path}")


    def openDirFile(e):
        file_path = f"{os.path.dirname(source.data)}\\BOS.xlsx"
        os.system(f"explorer /select,{file_path}")


    
    markinhoDown_open_file = Markdown(
        f"[Abrir o arquivo]({os.path.dirname(source.data)}\\BOS.xlsx)",
        code_style= TextStyle(size= 40),
        on_tap_link= openFile
    )


    icon_open_file_dir = IconButton(
        icon= icons.FILE_OPEN_ROUNDED,
        # icon_color= 
        icon_size= 26,
        tooltip= "Abrir na pasta",
        data= f"{os.path.dirname(source.data)}\\BOS.xlsx",
        on_click= openDirFile
    )


    completionDialog = AlertDialog(
        modal= True,
        title= Text("Sucesso", weight= "bold"),
        actions=[ ElevatedButton("OK", on_click= close_dlg) ],
        actions_alignment= "end",
        content=
            Row(
                wrap= True,
                controls= [
                    Row([
                            Icon(icons.CHECK_CIRCLE_ROUNDED, color= colors.GREEN),
                            Text("Extração concluida com sucesso!", size= 18)
                        ]
                    ),
                    Row(
                        alignment= MainAxisAlignment.CENTER,
                        spacing= 180,
                        controls= 
                        [
                            markinhoDown_open_file,
                            icon_open_file_dir,
                        ]
                    )
                ]
            ),
        
    )

    def open_dlg(e):
        page.dialog = completionDialog
        completionDialog.open = True
        page.update()

    select_style_btn = ButtonStyle(
        color={"": colors.WHITE},
        bgcolor={"": cores["yellow"]},
        surface_tint_color={"": colors.WHITE70},
        overlay_color={"": cores["sec_yellow_shade"]},
        shadow_color={"": cores["sec_yellow_shade"]},
        shape={"": RoundedRectangleBorder(radius=5)})

    extract_btn = ElevatedButton(
        text="Extrair", width=200,
        on_click= run,    #lambda _: page.go("/veriDuplicados"),
        style=ButtonStyle(
            color={"": colors.WHITE},
            bgcolor={"": cores["yellow"]},
            surface_tint_color={"": colors.WHITE70},
            overlay_color={"": cores["sec_yellow_shade"]},
            shadow_color={"": cores["sec_yellow_shade"]},
            shape={"": RoundedRectangleBorder(radius=6)},
        )
    )


    def activeVeriDupli(e):
        drpdwn_col.options= get_col()
        drpdwn_nbop.options= get_col(all_columns=True)
        page.go("/veriDuplicados")

    btnToVeriDupli = ElevatedButton(
        text="Verificar Duplicidade",
        on_click= activeVeriDupli,
        disabled= True,
        visible= False,
        style=ButtonStyle(
            color={"": colors.WHITE},
            bgcolor={"": cores["yellow"]},
            surface_tint_color={"": colors.WHITE70},
            overlay_color={"": cores["sec_yellow_shade"]},
            shadow_color={"": cores["sec_yellow_shade"]},
            shape={"": RoundedRectangleBorder(radius=6)},
        )
    )


    name_column_dropdown = Dropdown(
        hint_text="Escolha a coluna do relato:", width=350, height=59,
        autofocus=True, border_color=cores["yellow"], border_width=5,
        color=colors.BLACK,
        options=[dropdown.Option("Escolha a coluna do relato:")]
        )

    def on_dialog_event(e: FilePickerResultEvent):
        try:
            file = e.files[0].path
            source.value = file if len(file) <= 72 else file[:71] + '...'
            source.tooltip = file
            source.data = file
            colunas()
            page.update()
        except TypeError:
            pass

    # GUIA DO USUÁRIO
    def help_dlg(e):
        """GUIA DO USUÁRIO"""
        def close_dlg(e):
            helpDialog.open = False
            page.update()
        helpDialog = AlertDialog(
            modal=True,
            title=Text("Guia do Usuário:", text_align='center'),
            content=Column([
                Text("O que este extrator faz?", weight="bold"),
                Text("O extrator léxico de BOP é um sistema desktop, que tem por objetivo agilizar a extração de dados dos boletins de ocorrência, partindo da hipótese de que cada dado a ser extraído está em um padrão pré definido.\nOs dados extraídos são os listados a seguir: Nome Próprio, Aplicativo, Banco, Chave PIX, E-mail, Endereço, Valor monetário, Endereço eletrônico (URL), CPF/CNPJ, IMEI, Conta bancária e Número telefônico."),
                Text("Como funciona?", weight="bold"),
                Text("Selecione o arquivo de Boletim de ocorrência, que contenha a coluna dos relatos no qual será feita a extração dos dados.\nO arquivo será aceito somente nos formatos CSV ou XLSX (formato do Excel).\nSelecione o nome da coluna correspondente aos relatos, se por acaso não tiver nenhuma coluna selecionada, irá informar um erro para que você possa selecionar novamente.\n\nObservação: O arquivo extraído ficará na mesma pasta do arquivo selecionado."),
            ], scroll="auto"),
            actions=[ElevatedButton(
                "Entendido", width=200, height=25, on_click=close_dlg)],
            actions_alignment="center",
        )

        page.dialog = helpDialog
        helpDialog.open = True
        page.update()

    # Muda o tema de light <--> dark
    def chng_mode(e):
        page.theme_mode = "light" if page.theme_mode == "dark" else "dark"
        page.bgcolor = colors.BLACK if page.theme_mode == "dark" else cores["white_grey"]
        page.views[0].bgcolor = page.bgcolor

        select_style_btn.color, select_style_btn.bgcolor, select_style_btn.surface_tint_color, select_style_btn.overlay_color, select_style_btn.shadow_color = ({"": colors.YELLOW}, {"": "#191919"}, {"": colors.BLACK}, {                                                                                                                                                  "": "#191919"}, {"": "#191919"}) if page.theme_mode == "dark" else ({"": colors.WHITE}, {"": cores["yellow"]}, {"": colors.WHITE70}, {"": cores["sec_yellow_shade"]}, {"": cores["sec_yellow_shade"]})

        name_column_dropdown.color = colors.WHITE if page.theme_mode == "dark" else colors.BLACK
        drpdwn_col.color = colors.WHITE if page.theme_mode == "dark" else colors.BLACK
        drpdwn_nbop.color = colors.WHITE if page.theme_mode == "dark" else colors.BLACK

        extract_btn.style = ButtonStyle(
            color={"": colors.YELLOW}, bgcolor={"": "#191919"}, surface_tint_color={"": colors.BLACK}, overlay_color={"": "#191919"}, shadow_color={"": "#191919"}, shape={"": RoundedRectangleBorder(radius=6)}) if page.theme_mode == "dark" else ButtonStyle(
            color={"": colors.WHITE}, bgcolor={"": cores["yellow"]}, surface_tint_color={"": colors.WHITE70}, overlay_color={"": cores["sec_yellow_shade"]}, shadow_color={"": cores["sec_yellow_shade"]}, shape={"": RoundedRectangleBorder(radius=6)})
        
        btnToVeriDupli.style = ButtonStyle(
            color={"": colors.YELLOW}, bgcolor={"": "#191919"}, surface_tint_color={"": colors.BLACK}, overlay_color={"": "#191919"}, shadow_color={"": "#191919"}, shape={"": RoundedRectangleBorder(radius=6)}) if page.theme_mode == "dark" else ButtonStyle(
            color={"": colors.WHITE}, bgcolor={"": cores["yellow"]}, surface_tint_color={"": colors.WHITE70}, overlay_color={"": cores["sec_yellow_shade"]}, shadow_color={"": cores["sec_yellow_shade"]}, shape={"": RoundedRectangleBorder(radius=6)})

        button.style = ButtonStyle(
            color={"": colors.YELLOW}, bgcolor={"": "#191919"}, surface_tint_color={"": colors.BLACK}, overlay_color={"": "#191919"}, shadow_color={"": "#191919"}, shape={"": RoundedRectangleBorder(radius=6)}) if page.theme_mode == "dark" else ButtonStyle(
            color={"": colors.WHITE}, bgcolor={"": cores["yellow"]}, surface_tint_color={"": colors.WHITE70}, overlay_color={"": cores["sec_yellow_shade"]}, shadow_color={"": cores["sec_yellow_shade"]}, shape={"": RoundedRectangleBorder(radius=6)})

        icon_help.icon_color = colors.WHITE if page.theme_mode == "dark" else colors.BLACK
        theme_icon_button.selected = not theme_icon_button.selected
        page.update()
    
    theme_icon_button = IconButton(icons.DARK_MODE, selected_icon=icons.LIGHT_MODE, icon_color=colors.BLACK,
    icon_size=25, tooltip="Mudar tema", on_click=chng_mode, style=ButtonStyle(color={"": colors.BLACK, "selected": colors.WHITE}))



    def get_df(path_:str):
        try:
            # path_ = source.data
            if path_.endswith(".csv"):
                df = pd.read_csv(path_)
            elif path_.endswith(".xlsx"):
                df = pd.read_excel(path_, engine="openpyxl")
            return df

        except:
            pass

    def colunas():
        
        # if path_:
            # if path_.endswith(".csv"):
            #     df = pd.read_csv(path_)
            # elif path_.endswith(".xlsx"):
            #     df = pd.read_excel(path_, engine="openpyxl")

        # df = self.dataframe
        df = get_df(source.data)
        list_columns = list(df.columns)
        dropdown_options = [dropdown.Option(coluna) for coluna in list_columns]
        del(name_column_dropdown.options[1:])
        name_column_dropdown.options.extend(dropdown_options)

        page.update()
        return df


    # Icone do Guia de Usuario
    icon_help = IconButton(
        icon=icons.HELP, icon_color=colors.BLACK87, tooltip="Ajuda",
        on_click=help_dlg)

    file_picker = FilePicker(on_result=on_dialog_event)
    page.overlay.append(file_picker)
    page.update()

    # source = Text(value= "", data= "",
    #               size= 15, weight= "w400", italic= True, text_align= "center", no_wrap= True)


##=====================================================================================================================
## parte esquecida, dúvidas? Pode apagar...
    def minimize(e):
        page.window_minimized = True if page.window_minimized == False else False
        page.update()

    def full_screen(e):
        page.window_maximized = True if page.window_maximized == False else False
        e.control.selected = not e.control.selected
        page.update()


    dragPainel = Container(
        Row(
            [
                WindowDragArea(Container(Text(" "*4+"Extrator Léxico de BOP", size=16, weight="bold",
                color=colors.BLACK, expand=True), padding=padding.only(bottom=-1)), expand=True),
                IconButton(
                    icon=icons.MINIMIZE_SHARP,
                    icon_size=20,
                    style=ButtonStyle(
                        color={"": colors.BLACK},
                        bgcolor={"hovered": cores["yellow_transp"]},
                        shape={"": RoundedRectangleBorder(radius=0)}
                        ), on_click=minimize),

                IconButton(
                    icons.CROP_SQUARE_SHARP,
                    selected_icon=icons.AUTO_AWESOME_MOTION_SHARP,
                    selected=False,
                    icon_size=20,
                    style=ButtonStyle(
                    color={"":colors.BLACK},
                    bgcolor={"hovered":cores["yellow_transp"]},
                    shape={"": RoundedRectangleBorder(radius=0)}
                ), on_click=full_screen),

                IconButton(icons.CLOSE_SHARP,
                icon_size=20,
                style=ButtonStyle(
                    color={"": colors.BLACK},
                    bgcolor={"hovered": "#99fff0000",
                    "": colors.TRANSPARENT},
                    shape={"": RoundedRectangleBorder(radius=0)}
                    ), on_click=lambda _: page.window_close())
            ]
        ), bgcolor=colors.YELLOW, height=30
    )

 ##====================================================================================================================




    def duplicidade(file_path:str="", column:str="", col_nbop:str=""):
        column:str = drpdwn_col.value
        col_nbop:str = drpdwn_nbop.value
        

        file = get_df( f"{os.path.dirname(source.data)}\\BOS.xlsx" ).filter(items=[column, col_nbop])

        file[column] = file[column].apply(lambda x: str(x).split(", ") if x not in [nan, "nan", "NaN"] else x )
        # file = file.dropna(subset=[column])
        file = file.explode(column)


        dupli = file [file.duplicated([column], keep=False) ]
        dupli_gp = dupli.groupby(by=[column])[col_nbop].apply(lambda x: " | ".join(x)).reset_index()

        dict_dupli: dict = dict( zip( dupli_gp[column], dupli_gp[col_nbop] ) )
        

        lists_textos = texts_duplicate(dict_dupli)
        col.controls = lists_textos
        page.update()

    def texts_duplicate(df_dupli:dict) -> list[Text]:
        list_texts: list = []
        for e, keys in enumerate(df_dupli):
            list_texts.append( 
                Row(
                controls=[
                    Container(
                        bgcolor= "#b0b0b0" if (not e&1) else colors.SURFACE_VARIANT, #"#c6c6c6" "#fafafa"
                        opacity= 1,
                        width= page.window_width/3,
                        height= 40,
                        margin= margin.all(2),
                        padding= padding.only(left=10),
                        content= Row(
                            spacing= 20,
                            scroll= "adaptive",
                            height= 20,
                            controls=[
                            Text(
                                value= keys,
                                selectable=True,
                                size= 18
                            )
                        ])
                    ),
                    Container(
                        bgcolor= "#b0b0b0" if (not e&1) else colors.SURFACE_VARIANT,
                        opacity = 1,
                        height= 40,
                        expand= True,
                        margin= margin.all(2),
                        padding= padding.only(left=10),
                        content= Row(
                            spacing= 20,
                            scroll= "adaptive",
                            height= 20,
                            controls=[
                                Text(
                                value= df_dupli[keys],
                                selectable=True,
                                size=20
                                )
                            ]
                        ),
                    )
                ])
            )
        return list_texts


    def get_col(all_columns:bool= False):
        file_ = get_df( f"{os.path.dirname(source.data)}\\BOS.xlsx" )
        
        
        # list_columns = list(df.columns)
        # dropdown_options = [dropdown.Option(coluna) for coluna in list_columns]
        # del(name_column_dropdown.options[1:])
        # name_column_dropdown.options.extend(dropdown_options)

        # page.update()
        # return df


        if file_ is not None:
            list_colDupli: list[str] = list(file_.columns[ 0 if all_columns else list(file_.columns).index("NOMES") : ])
            _drpdwn_optns: list[flet.Option] = [ dropdown.Option(column) for column in list_colDupli ]

        else:
            _drpdwn_optns = []
        # page.update()
        return _drpdwn_optns

    drpdwn_col = Dropdown(
            hint_text= "Selecione uma coluna a ser analisada",
            text_size= 16,
            width= page.window_width*0.6,
            height= 60, autofocus= True,
            border_color= cores["yellow"], border_width= 5,
            color= colors.BLACK,
            options= [] #get_col() #[dropdown.Option("Selecione a coluna extraída")] + 
        )

    drpdwn_nbop = Dropdown(
            hint_text= "Selecione a coluna do número de boletim",
            text_size= 16,
            width= page.window_width*0.6,
            height= 60, autofocus= True,
            border_color= cores["yellow"], border_width= 5,
            color= colors.BLACK,
            options= [] # get_col(all_columns=True) #[dropdown.Option("Selecione a coluna extraída")] + 
        )

    col = Column(
            controls= None,
            spacing= 2,
        )

    button = ElevatedButton(
            text="Verificar", width=360,
            on_click=duplicidade,
            style=ButtonStyle(
                color={"": colors.WHITE},
                bgcolor={"": cores["yellow"]},
                surface_tint_color={"": colors.WHITE70},
                overlay_color={"": cores["sec_yellow_shade"]},
                shadow_color={"": cores["sec_yellow_shade"]},
                shape={"": RoundedRectangleBorder(radius=6)},
            )
        )

    def view_pop(e):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    def route_change(e):
        page.views.clear()
        page.views.append(
            View(
                bgcolor= page.bgcolor,
                padding= 0,
                route= "/",
                controls= [
                Container(
                    content=
            
                    Column(
                        alignment= MainAxisAlignment.CENTER,
                        horizontal_alignment= CrossAxisAlignment.CENTER,
                        controls= 
                        [

                            ## Header Logo
                            Container(
                                height= 80,
                                bgcolor= cores['grey'],
                                margin= margin.only(bottom= -80), #page.window_height*0.14
                                content=
                                    Row(
                                        alignment= MainAxisAlignment.CENTER,
                                        controls=
                                            [
                                                Image(src= "/logo_pc-100x100.png", width= 60, height= 60),
                                                Image(src= "/logo_pcpa_label.png", height= 60)
                                            ]
                                    ),
                            ),

                            ## Body
                            Column(
                                height= page.window_height,
                                width= page.window_width,
                                alignment= MainAxisAlignment.CENTER,
                                horizontal_alignment= CrossAxisAlignment.CENTER,
                                controls=
                                [
                                    
                                    # Botões ícones de Dark Mode && do Guia do Usuário
                                    Container(
                                        content=
                                            Row(
                                                width= page.window_width*0.62,
                                                alignment= MainAxisAlignment.END,
                                                controls= 
                                                [
                                                    theme_icon_button,
                                                    icon_help,
                                                ]
                                            ),
                                    ),

                                    # Texto XLSX/CSV && Botão de seleção do arquivo
                                    Container(
                                        content=
                                            Column(
                                                [
                                                    Text(value= 'Arquivo XLSX ou CSV:', size= 16, weight= "bold"),
                                                    ElevatedButton("Selecione o arquivo", width=350, height=40,
                                                    on_click= lambda _: file_picker.pick_files(
                                                        allowed_extensions= ["xlsx", "csv"], allow_multiple= False,
                                                        dialog_title= "Arquivo"), style= select_style_btn),
                                                ]
                                            )
                                    ),
                                    

                                    # Texto Path do arquivo selecionado
                                    Container(
                                        height= 40, alignment= alignment.center,
                                        # margin= margin.only(top= -8, bottom= 8),
                                        content=
                                            ResponsiveRow([source])
                                    ),

                                    # Texto Coluna relato && Dropdown
                                    Container(
                                        content=
                                            Column(
                                                [
                                                    Text(value="Coluna do relato:", size=16, weight="bold"),
                                                    name_column_dropdown
                                                ]
                                            )
                                    ),

                                    # Botão de Extração e de Verificar Duplicados
                                    Row(
                                        alignment= MainAxisAlignment.CENTER,
                                        controls=
                                            [
                                                btnToVeriDupli,
                                                extract_btn,
                                            ]
                                    ),

                                    # ProgressRing
                                    Container(
                                        margin= margin.only(top= 15, bottom= 15),
                                        width= page.window_width*0.62,
                                        alignment= alignment.center,
                                        content=
                                            my_precious,
                                    ),

                                ] #// Controls Column Body
                            ), #// Column Body

                        ] # // Controls Column 
                    ) #// Column

                ) #// Container
                ] #// Controls View
            ) #// View
        ) #// append
        page.update()
        if page.route == "/veriDuplicados":
            page.views.append(
                View(
                    bgcolor= page.bgcolor,
                    padding= padding.only(left= 20, right= 20),
                    scroll= "adaptive",
                    route= "/veriDuplicados",
                    controls= [
                        # Column([dragPainel], alignment="center", horizontal_alignment="center"),
                        AppBar(
                            # actions= [],
                            title= Text("Verificar a duplicidade de dados:", size= 26),
                            center_title= True,
                            bgcolor= colors.SURFACE_VARIANT,
                            leading= IconButton(icon= icons.ARROW_BACK, tooltip= "Voltar",
                                on_click= lambda _: page.go("/"),
                            )
                        ),
                        Container(content=
                            Column(controls=
                                [
                                    # Texto Coluna NBOP && Dropdown
                                    ResponsiveRow(
                                        [
                                            Text("Selecione a coluna do número de Boletim de ocorrência: ",
                                                size= 16, weight="bold"
                                            ), 
                                            drpdwn_nbop,
                                        ]
                                    ),

                                    # Texto Coluna análise && Dropdown
                                    ResponsiveRow(
                                        [
                                            Text("Selecione a coluna desejada para a análise: ",
                                                size= 16, weight="bold"
                                            ),
                                            drpdwn_col,
                                        ]
                                    ),
                                    # Botão de verificação
                                    ResponsiveRow([button])

                                ] #// Controls Column
                            ), #// Column

                        ), #// Container
                        # Data Visualization
                        col

                    ] #// Controls View
                ) #// View
            )
            page.update()


    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


path_abs = os.path.split(os.path.realpath(os.path.basename(sys.argv[0])))[0]
flet.app(target=main,
         assets_dir=Path(r"./images/") )
#view = flet.WEB_BROWSER,

# DEV LEMBRETE :)
# print(sys.argv[0]) #RETURN THE FULL PATH WITH THE NAME OF FILE
# print(os.path.basename(sys.argv[0])) #RETURN ONLY THE NAME OF FILE
