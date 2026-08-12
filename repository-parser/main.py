import json
from parser import parse_repository


def main():
    repo_url = input("Enter GitHub repository URL: ")

    result = parse_repository(repo_url)

    print("\nRepository Analysis:")
    print(json.dumps(result, indent=4))

    with open("repository_metadata.json", "w") as file:
        json.dump(result, file, indent=4)

    print("\nMetadata saved to repository_metadata.json")


if __name__ == "__main__":
    main()