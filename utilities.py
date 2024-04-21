import pandas as pd


def read_data(spreadsheet):
    try:
        # Attempt to read the data using pandas.read_excel
        df = pd.read_excel(spreadsheet)
        rows = []

        for index, row in df[['Name', 'Org', 'Amount', 'Date']].iterrows():
            rows.append({'Name': row['Name'],
                    'Org': row['Org'],
                    'Amount': row['Amount'],
                    'Date': row['Date'],
                    })
        
        return rows
            
    except FileNotFoundError:

        # Handle case where file doesn't exist
        print(f"Error: File '{spreadsheet}' not found.")
        return None  # Return None to indicate an error

    except pd.errors.ParserError:

        # Handle case where file format is unsupported
        print(f"Error: Unable to parse '{spreadsheet}'. Invalid format?")
        return None  # Return None to indicate an error