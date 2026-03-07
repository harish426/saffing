## Installation

```bash
pip install "fastapi[standard]"
```

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
``` 









docker run `
>> --name backend `
>> --network beckend-network `
>> -e DATABASE_URL="" `
>> -e GEMINI_API_KEY="" `
>>  -p 3000:3000 marketing-backend