from collections import defaultdict
import numpy as np
import pdfplumber
import os
import json
import datetime
import random

""" 
This pipeline serves as a preprocessing script for 8D reports, to make them more digestable for LLMs

"""

def read_tabular_pdf(file_dir):
    """
    Reads a PDF file and extracts tables from it using pdfplumber. Returns a list of tables, where each table is represented as a list of rows, and each row is a list of cell values.
    """
    print(f"Processing {file}...")
    try:
        with pdfplumber.open(file_dir) as pdf:
            #table_pdf = pdf.pages[0].extract_tables()+pdf.pages[1].extract_tables()
            table_pdf = []
            for table in pdf.pages:
                table_pdf += table.extract_tables()
    except Exception as e:
        print(f"Failed processing {file}: {e}")
    
    table_compressed = []
    for table in table_pdf:
        for t in table:
            if any(x not in (None, "") for x in t):
                table_compressed.append(t)
    return table_compressed

def normalize(text):
    """
    Normalizes strings
    """
    return " ".join(str(text).strip().upper().split())

def split_sections(rows, header_map):
    """
    Splits the rows into sections based on the header_map and returns a dictionary where keys are section names and values are lists of rows for that section.
    """
    cleaned_rows = [lst for lst in rows if any(x not in (None, "") for x in lst)]
    sections = []
    current_header = None
    current_rows = []

    for row in cleaned_rows:
        if not row:
            continue
        # check if this row starts a new section
        first_cell = normalize(row[0])
        clean_row = [x for x in row if x not in (None, "")] # maybe dont need clean_row
        if first_cell in header_map:
            # save previous section
            if current_header is not None:
                sections.append((current_header, current_rows))

            # map to your desired header name
            current_header = header_map[first_cell]
            current_rows = [row]
            continue
        try:
            header_cell = normalize(clean_row[1])
            if header_cell in header_map:
                # save previous section
                if current_header is not None:
                    sections.append((current_header, current_rows))

                # map to your desired header name
                current_header = header_map[header_cell]
                current_rows = [row]

            else:
                if current_header is not None:
                    current_rows.append(row)
        except IndexError:
            if current_header is not None:
                    current_rows.append(row)
            pass

    # add last section
    if current_header is not None:
        sections.append((current_header, current_rows))

    return sections

def split_sections_dict(rows, header_map):
    """
    Calls split_sections and organizes the result into a dictionary where keys are section names and values are lists of rows for that section.
    """
    result = defaultdict(list)

    for header, section_rows in split_sections(rows, header_map):
        result[header].append(section_rows)
    return dict(result)

def parse_meta_data(section_md):
    """ Meta Data parsing """
    headers_md = [x.replace("\n", " ") for x in section_md[0]]
    values_md = [x for x in section_md[1]]
    dict_md = dict(zip(headers_md, values_md))
    dict_md[section_md[6][0].replace("\n", " ")] = section_md[7][0] # Should these be translated??
    for i in range(8, len(section_md)-1):
        dict_md[section_md[i][0].replace("\n", " ")] = section_md[i][2]

    return dict_md

def parse_d1(section_d1):
    """ D1 parsing """
    headers_d1 = [x.replace("\n", " ") for x in section_d1[1] if x is not None]
    dict_d1 = {}
    for i in range(2, len(section_d1)):
        values_d1 = [x for x in section_d1[i] if x is not None]
        member_dict = dict(zip(headers_d1, values_d1))
        dict_d1[f'member_{i-1}'] = member_dict
    return dict_d1

def parse_d2(section_d2):
    """ D2 parsing """
    dict_d2 = {}
    for i in range(1, len(section_d2)):
        dict_d2[section_d2[i][0].replace("\n", " ")] = section_d2[i][2].replace("\n", " ") # TRANSLATION ??
    return dict_d2

def parse_d3(section_d3):
    """ D3 parsing """
    headers_d3 = [x.replace("\n", " ") for x in section_d3[1][1:] if x is not None]
    dict_d3 = {}
    for i in range(2, len(section_d3)):
        values_d3 = [x.replace("\n", " ") for x in section_d3[i][1:] if x is not None]
        if any(values_d3):
            dict_d3[f'action_{i-1}'] = dict(zip(headers_d3, values_d3))
    return dict_d3

def parse_d4(section_d4):
    """ D4 parsing """
    return {section_d4[0][2]: section_d4[1][0].replace("\n", " ")}

def parse_d5(section_d5):
    """ D5 parsing """
    headers_d5 = [x.replace("\n", " ") for x in section_d5[1][1:] if x is not None]
    dict_d5 = {}
    for i in range(2, len(section_d5)):
        values_d5 = [x.replace("\n", " ") for x in section_d5[i][1:] if x is not None]
        if any(values_d5):
            dict_d5[f'corrective_action_{i-1}'] = dict(zip(headers_d5, values_d5))
    return dict_d5
    
def parse_d8(section_d8):
    """ D8 parsing """
    dict_d8_sub = {}
    headers_d8 = [x.replace("\n", " ") for x in section_d8[2][1:] if x is not None]
    for i in range(3, 7):
        values_d8 = [x.replace("\n", " ") for x in section_d8[i][1:] if x is not None]
        if any(values_d8):
            dict_d8_sub[f'closure_{i-2}'] = dict(zip(headers_d8, values_d8))
    dict_d8 = {'Closure': dict_d8_sub}
    dict_d8[section_d8[7][1]] = "DOUBLE CHECK THIS" # double check this
    return dict_d8

if __name__ == "__main__":
    # Define file paths and section headers, these variables will need to be adjusted to a config format
    curr_dir = os.getcwd()
    DATA_DIR = os.path.join(curr_dir, "data")
    JSON_DIR = os.path.join(curr_dir, "processed_data")
    #file = "8D_Cooperoeste_RNC 04-26_Contaminação física.pdf"

    SECTION_HEADERS = [
        'SIG SAP',
        'Define the Team\nAdd all members of the team, update as required through the steps.',
        'Problem Definition / Analysis',
        'Containment Actions',
        'Root Cause Analysis/ Statement',
        'Corrective Actions (CA)',
        'Preventive Measures (PM)', # Missing in some files, but we can still extract the section if it exists
        'Corrective Actions & Preventive Measures (CA&PM) Validation',
        'Closure'

    ]
    SECTION_NAMES = [
        'meta_data',
        'D1_team',
        'D2_problem_definition',
        'D3_containment_actions',
        'D4_root_cause_analysis',
        'D5_corrective_actions',
        'D6_preventive_measures',
        'D7_validation',
        'D8_closure'
    ]
    HEADER_MAP = {
        normalize(pdf): target
        for pdf, target in zip(SECTION_HEADERS, SECTION_NAMES)
    }

    for file in os.listdir(DATA_DIR):    
        # Tabular data extraction from pdf files
        file_dir = os.path.join(DATA_DIR, file)
        table_pdf = read_tabular_pdf(file_dir)

        # Section splitting
        sections = split_sections_dict(table_pdf, HEADER_MAP)
        
        # Header extraction: meta_data
        section_md = sections['meta_data'][0]
        dict_md = parse_meta_data(section_md)

        # Header extraction: D1_team
        section_d1 = sections['D1_team'][0]
        dict_d1 = parse_d1(section_d1)

        # Header extraction: D2_problem_definition
        section_d2 = sections['D2_problem_definition'][0]
        dict_d2 = parse_d2(section_d2)

        # Header extraction: D3_containment_actions
        section_d3 = sections['D3_containment_actions'][0]
        dict_d3 = parse_d3(section_d3)

        # Header extraction: D4_root_cause_analysis
        section_d4 = sections['D4_root_cause_analysis'][0]
        dict_d4 = parse_d4(section_d4) # TRANSLATION ??

        # Header extraction: D5_corrective_actions
        section_d5 = sections['D5_corrective_actions'][0]
        dict_d5 = parse_d5(section_d5)

        # Header extraction: D6_preventive_measures
        try:
            section_d6 = None#sections['D6_preventive_measures'][0]
        except KeyError:
            print(f"No preventive measures section found in file {file}")
            dict_d6 = None

        # Header extraction: D7_validation
        section_d7 = sections['D7_validation'][0]

        headers_d7 = [x.replace("\n", " ") for x in section_d7[1][1:] if x is not None]
        dict_d7 = {}
        for i in range(2, len(section_d7)):
            values_d7 = [x.replace("\n", " ") for x in section_d7[i][1:] if x is not None]
            if any(values_d7):
                dict_d7[f'validation_{i-1}'] = dict(zip(headers_d7, values_d7))

        # Header extraction: D8_closure
        section_d8 = sections['D8_closure'][0]
        dict_d8 = parse_d8(section_d8)

        dict_json = {}
        final_dicts = [dict_md, dict_d1, dict_d2, dict_d3, dict_d4, dict_d5, dict_d7, dict_d8]  # | (dict_d6 if dict_d6 is not None else {})
        for key, section_dict in zip(SECTION_NAMES, final_dicts):
            dict_json[key] = section_dict
    

        # Save extracted data to JSON file
        time_stmp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = os.path.join(JSON_DIR, f"8D_report_{random.randint(1,100)}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dict_json, f, ensure_ascii=False, indent=4)
