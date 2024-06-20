### Website of the Training and Placement Cell,
##### Department of Computer Science and Engineering, Assam University, Silchar


[**Visit Production Branch**](https://github.com/HimDek/TPC-WebSite/tree/production)

[**Visit Website**](https://tpc-cse-aus.vercel.app/)

#### Prerequisites

1. python and pip and git should be installed on the system

    To Check execute in Command line:

      ```
      python --version
      pip --version
      git --version
      ```

#### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/Training-and-Placement-Cell-CSE-AUS/TPC-WebSite.git
    ```

2. Create a virtual environment:

    ```bash
    python -m venv env
    ```

3. Activate the virtual environment:

    - For Windows:

      ```bash
      .\env\Scripts\activate
      ```

    - For macOS/Linux:

      ```bash
      source env/bin/activate
      ```

4. Change current directory to `.\src\`:

    - For Windows:

      ```bash
      CD src
      ```

    - For macOX/Linux:

      ```bash
      cd src
      ```

5. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

6. Run database migrations:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

#### Usage

1. Start the development server:

    ```bash
    python manage.py runserver
    ```

2. Open your web browser and visit `http://localhost:8000`.
