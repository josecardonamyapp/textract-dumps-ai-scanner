from tabulate import tabulate


class TextractLayoutParser:
    def __init__(self, textract_json, table_format, exclude_figure_text):
        self.data = textract_json
        self.table_format = table_format
        self.exclude_figure_text = exclude_figure_text

    def get_text(self):
        pages = {}
        blocks_map = {}
        line_ids_in_tables = set()
        word_id_to_line_id = {}

        # Crear un mapa de bloques por ID y mapear palabras a líneas
        for block in self.data['Blocks']:
            blocks_map[block['Id']] = block
            page_number = block['Page']
            if block['BlockType'] == 'LINE':
                if page_number not in pages:
                    pages[page_number] = {'non_table_text': [], 'tables': []}
                for relationship in block.get('Relationships', []):
                    if relationship['Type'] == 'CHILD':
                        for word_id in relationship['Ids']:
                            word_id_to_line_id[word_id] = block['Id']

        # Procesar tablas y recopilar IDs de líneas dentro de tablas
        for block in self.data['Blocks']:
            if block['BlockType'] == 'TABLE':
                page_number = block['Page']
                if page_number not in pages:
                    pages[page_number] = {'non_table_text': [], 'tables': []}
                table = []
                for relationship in block.get('Relationships', []):
                    if relationship['Type'] == 'CHILD':
                        for cell_id in relationship['Ids']:
                            cell = blocks_map[cell_id]
                            if cell['BlockType'] == 'CELL':
                                row_index = cell['RowIndex'] - 1
                                col_index = cell['ColumnIndex'] - 1
                                while len(table) <= row_index:
                                    table.append([])
                                while len(table[row_index]) <= col_index:
                                    table[row_index].append('')
                                cell_text = ''
                                for cell_relationship in cell.get('Relationships', []):
                                    if cell_relationship['Type'] == 'CHILD':
                                        for word_id in cell_relationship['Ids']:
                                            word = blocks_map[word_id]
                                            if word['BlockType'] == 'WORD':
                                                cell_text += word['Text'] + ' '
                                                # Registrar el ID de línea asociado a la palabra
                                                line_id = word_id_to_line_id.get(
                                                    word_id)
                                                if line_id:
                                                    line_ids_in_tables.add(
                                                        line_id)
                                table[row_index][col_index] = cell_text.strip()
                pages[page_number]['tables'].append(table)

        # Procesar líneas que no están en tablas
        for block in self.data['Blocks']:
            if block['BlockType'] == 'LINE' and block['Id'] not in line_ids_in_tables:
                page_number = block['Page']
                if page_number not in pages:
                    pages[page_number] = {'non_table_text': [], 'tables': []}
                pages[page_number]['non_table_text'].append(block['Text'])

        # Formato de salida
        output = {}
        for page_num, content in pages.items():
            non_table_text = '\n'.join(content['non_table_text'])
            tables_tabulated = []
            for table in content['tables']:
                tabulated_table = tabulate(table, tablefmt='pipe')
                tables_tabulated.append(tabulated_table)
            output[str(page_num)] = {
                'non_table_text': non_table_text,
                'tables_tabulated': tables_tabulated
            }

        return output
