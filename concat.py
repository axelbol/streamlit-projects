import pandas as pd
import os

# Function to get the list of processed files from the output CSV file (if it exists)
def get_processed_files(output_file):
    try:
        existing_df = pd.read_csv(output_file)
        return existing_df['source_file'].unique().tolist()  # Assuming 'source_file' column stores the source filenames
    except FileNotFoundError:
        return []

# Function to concatenate new CSV files
def concatenate_csv_files(folder_path, output_file):
    processed_files = get_processed_files(output_file)
    df_list = []

    # Loop through each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv') and filename not in processed_files:
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            df['source_file'] = filename  # Add a column to track the source file name
            if not df.empty:  # Ensure the DataFrame is not empty before adding NEW LINE
                df_list.append(df)
                print(f"Adding new file: {filename}")

    if not df_list:
        print("No new files to append.")
        return

    # Filter out empty DataFrames explicitly (for future compatibility) NEW LINE
    df_list = [df for df in df_list if not df.empty]

    if df_list: # Ensure df_list still has data after filtering NEW LINE
        # Concatenate new DataFrames
        df_new = pd.concat(df_list, ignore_index=True)

        # Append to existing file or create a new one
        try:
            # If the file exists, append without the header
            # df_new.to_csv(output_file, mode='a', header=False, index=False)
            df_new.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False) # Write header only if the file does not exist NEW LINE
            print(f"Appended new data to {output_file}")
        except FileNotFoundError:
            # If the file doesn't exist, create it with the header
            df_new.to_csv(output_file, index=False)
            print(f"Created new concatenated file {output_file}")
    else: # NEW LINE
        print("No new data to concatenate")

if __name__ == '__main__':

    folder_path = '/home/axel/Code/Python/axel/streamlit/csv'
    output_file = '/home/axel/Code/Python/axel/streamlit/concat_files/concat_shots.csv'

    # Run the concatenation
    concatenate_csv_files(folder_path, output_file)
