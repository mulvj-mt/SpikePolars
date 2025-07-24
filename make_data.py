import csv
import random
import string
import os
import json


def generate_random_string(min_string_len=10, max_string_len=25):
    length = random.randint(min_string_len, max_string_len)
    letters = string.ascii_lowercase + string.digits
    return "".join(random.choice(letters) for i in range(length))


def gen_random_int(min_int_val=1, max_int_val=1000000):
    return random.randint(min_int_val, max_int_val)


def generate_schema(headers: list[str]) -> dict[str, str]:
    schema = {}
    for h in headers:
        if h == "id":
            schema[h] = "number"
        elif random.random() < 0.7:
            schema[h] = "string"
        else:
            schema[h] = "number"
    return schema


def save_schema(schema: dict[str, str]) -> bool:
    with open("schema.json", "w") as schema_file:
        json.dump(schema, schema_file)
    return True


def generate_id() -> int:
    if random.random() < 0.0001:
        return -1
    else:
        return gen_random_int(10000000, 1000000000)


def make_row(schema: dict) -> list:
    data = []
    for k, s in schema.items():
        if k == "id":
            data.append(generate_id())
        else:
            func = generate_random_string if s == "string" else gen_random_int
            data.append(func())
    return data


def generate_fake_csv(filename="fake_data.csv", num_columns=779, target_gb=1.5):
    """
    Generates a fake CSV file with a specified number of columns and target size.
    Data types are randomly chosen between text and integers.
    """
    separator = "|"

    # Estimate average row size for calculation
    avg_cell_size = 17.5
    estimated_row_size = (num_columns * avg_cell_size) + (num_columns - 1)

    # Convert target GB to bytes
    target_bytes = target_gb * 1024 * 1024 * 1024

    # Calculate approximate number of rows needed
    num_rows = int(target_bytes / estimated_row_size)
    # Add a buffer, as the estimation can be off
    num_rows = int(num_rows * 1.2)  # 20% buffer

    print(f"Estimated rows to generate: {num_rows}")

    # Generate column headers
    headers = ["id"] + [
        f"column_{i}_{generate_random_string(5)}" for i in range(num_columns)
    ]

    schema = generate_schema(headers)
    saved_schema = save_schema(schema)

    if not saved_schema:
        print("Schema generation failed")
        raise RuntimeError("Schema generation failed")
    print("Schema generated and saved")

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=separator)
        print("Generating data...")
        writer.writerow(headers)

        for i in range(num_rows):
            row_data = make_row(schema)
            writer.writerow(row_data)

            if (i + 1) % 1000 == 0:
                message = f"Generated {i} rows"
                print(message, flush=True, end="\r")

    print(f"File '{filename}' created successfully.")
    print(f"Final file size: {os.path.getsize(filename) / (1024 * 1024 * 1024):.2f} GB")


# Run the function to generate the file
if __name__ == "__main__":
    generate_fake_csv()
