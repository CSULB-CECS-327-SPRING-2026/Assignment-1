# Housing Search System - Three-Tier Architecture

A distributed housing search service implementing a three-tier architecture with TCP socket communication.

## System Architecture

```
┌─────────────┐       TCP        ┌─────────────────┐       TCP        ┌─────────────────┐
│             │ ───────────────► │                 │ ───────────────► │                 │
│   Client    │   Port 7100      │  App Server     │   Port 6000      │  Data Server    │
│ (client.py) │ ◄─────────────── │ (app_server.py) │ ◄─────────────── │(data_server.py) │
│             │                  │                 │                  │                 │
└─────────────┘                  │  • Caching      │                  │  • JSON Storage │
                                 │  • Ranking      │                  │  • Filtering    │
                                 │  • Logging      │                  │                 │
                                 └─────────────────┘                  └─────────────────┘
```

## Files

| File               | Description                                          |
|--------------------|------------------------------------------------------|
| `data_server.py`   | Data layer - manages housing database in JSON format |
| `app_server.py`    | Application layer - caching, ranking, logging        |
| `client.py`        | User interface - command-line client                 |
| `listings.json`    | Housing data (24 listings across 6 cities)           |

## Quick Start

### 1. Start the Data Server (Terminal 1)

```bash
python data_server.py
```

Default port: 6000

### 2. Start the Application Server (Terminal 2)

```bash
python app_server.py
```

Default port: 7100 (connects to Data Server on 6000)

### 3. Run the Client (Terminal 3)

```bash
python client.py
```

## Command Line Options

### Data Server
```bash
python data_server.py [port] [data_file]

# Examples:
python data_server.py 5001                    # Default settings
python data_server.py 6001 my_listings.json   # Custom port and file
```

### Application Server
```bash
python app_server.py [app_port] [data_port] [--no-cache]

# Examples:
python app_server.py                     # Default (port 5000, cache enabled)
python app_server.py 5000 5001 --no-cache  # Disable caching
```

### Client
```bash
python client.py [host] [port] [--perf-test [iterations]]

# Examples:
python client.py                    # Interactive mode
python client.py --perf-test 50     # Performance test with 50 iterations
```

## Client Commands

| Command                                | Description                  |
|----------------------------------------|------------------------------|
| `LIST`                                 | Show all available listings  |
| `SEARCH city=<City> max_price=<Price>` | Search by city and max price |
| `QUIT`                                 | Exit the client              |

### Example Session

```
Enter command: SEARCH city=LongBeach max_price=2500

================================================================================
 Found 5 listing(s)  |  Response time: 3.45ms
================================================================================
ID     City            Address                        Price      Beds
------ --------------- ------------------------------ ---------- ------
2      LongBeach       456 Seaside Ave                    $1800      1
5      LongBeach       321 Beach Blvd                     $1950      2
23     LongBeach       555 Atlantic Ave                   $2100      2
1      LongBeach       123 Ocean Blvd                     $2200      2
4      LongBeach       999 Pine Ave                       $2400      3
================================================================================
```

## Performance Testing

### Without Caching
```bash
# Terminal 2 - Start app server without cache
python app_server.py 5000 5001 --no-cache

# Terminal 3 - Run performance test
python client.py --perf-test 50
```

### With Caching
```bash
# Terminal 2 - Start app server with cache (default)
python app_server.py

# Terminal 3 - Run performance test
python client.py --perf-test 50
```

## Protocol Specification

### Client ↔ Application Server (CAS Protocol)

**Requests:**
- `LIST\n` - Return all listings
- `SEARCH city=<City> max_price=<Int>\n` - Search with filters
- `QUIT\n` - Close connection

**Responses:**
```
OK RESULT <n>\n
id=<id>;city=<city>;address=<addr>;price=<price>;bedrooms=<beds>\n
... (n lines)
END\n
```
or
```
ERROR <message>\n
```

### Application Server ↔ Data Server (ADS Protocol)

**Requests:**
- `RAW_LIST\n` - Return all listings
- `RAW_SEARCH city=<City> max_price=<Int>\n` - Filter by city and price

**Responses:** Same format as CAS Protocol

## Features

### Caching (Application Server)
- LRU (Least Recently Used) cache with configurable size
- Cache key: full command string (e.g., "SEARCH city=LongBeach max_price=2500")
- Cache statistics logged to console

### Ranking
Results are sorted by:
1. Price (ascending) - cheaper listings first
2. Bedrooms (descending) - more bedrooms preferred at same price

### Logging (Interceptor Pattern)
All requests and responses are logged to `app_server.log`:
- Timestamps
- Client addresses
- Commands received
- Responses sent
- Cache hit/miss status
- Response times

## Available Cities

The sample dataset includes listings in:
- LongBeach (6 listings)
- LA (5 listings)
- SanDiego (3 listings)
- SanFrancisco (3 listings)
- Irvine (3 listings)

## Troubleshooting

**"Cannot connect to server"**
- Ensure servers are started in order: Data Server first, then App Server
- Check that ports are not in use by other applications

**"Connection refused"**
- The target server is not running
- Check port numbers match between components

**Slow responses**
- First request may be slower (cache miss)
- Subsequent identical queries should be faster (cache hit)