# 🚀 Dexlyn Perpetuals Trading Bot - Complete Documentation

## 📖 Table of Contents
1. [Overview](#-overview)
2. [Quick Start](#-quick-start)
3. [Configuration Files](#-configuration-files)
4. [Order Field Reference](#-order-field-reference)
5. [Trading Strategies](#-trading-strategies)
6. [Advanced Features](#️-advanced-features)
7. [Test Execution Commands](#-test-execution-commands)
8. [Troubleshooting](#-troubleshooting)

## 🎯 Overview

The Dexlyn Perpetuals Trading Bot is a fully customizable automated trading system that interacts with Dexlyn perpetual contracts via the Supra CLI. It supports complete customization of every order parameter through JSON configuration files.

### Key Features
- ✅ **No Coding Required** - Everything configurable via JSON
- ✅ **Complete Field Control** - Every order parameter customizable
- ✅ **Multi-Network Support** - Testnet and Mainnet ready
- ✅ **Risk Management** - Stop loss, take profit, position sizing
- ✅ **Flexible Strategies** - Pre-built and custom strategies
- ✅ **Cross-Platform** - Windows, macOS, Linux support

## 🚀 Quick Start

### Step 1: Installation
```bash
# Clone or download the bot files
# Install dependencies
pip install pexpect wexpect python-dotenv
```

### Step 2: Generate Configuration Files
```bash
python dexlyn_bot.py --generate-configs
```
This creates:
- `config.json` - Main settings
- `network.json` - Network configurations
- `wallets.json` - Your wallet addresses
- `pairs.json` - Trading pairs
- `strategies.json` - Trading strategies
- `field_reference.json` - Complete field documentation

### Step 3: Configure Your Settings

**Edit `wallets.json`:**
```json
{
  "my_wallet": {
    "address": "0xYOUR_WALLET_ADDRESS_HERE",
    "profile": "your_supra_profile_name",
    "description": "My trading wallet"
  }
}
```

**Set Environment Variable:**
```bash
# Linux/macOS
export SUPRA_CLI_PASSWORD='your#password'

# Windows (Command Prompt)
set SUPRA_CLI_PASSWORD=your#password

# Windows (PowerShell)
$env:SUPRA_CLI_PASSWORD="your#password"
```

### Step 4: Run the Bot
```bash
# Basic test run
python dexlyn_bot.py --strategy basic_cycle --cycles 1

# Continuous trading
python dexlyn_bot.py --strategy basic_cycle

# Custom strategy
python dexlyn_bot.py --custom-config my_strategy.json
```

## 📁 Configuration Files

### 1. config.json - Main Configuration
```json
{
  "network": "testnet",
  "default_strategy": "basic_cycle",
  "trading": {
    "default_size_usd": 100.0,
    "default_collateral_usd": 50.0,
    "default_leverage": 2.0,
    "max_position_size_usd": 1000.0,
    "min_position_size_usd": 10.0
  },
  "orders": {
    "default_slippage_tolerance": 0.01,
    "default_timeout_seconds": 240,
    "confirmation_attempts": 3,
    "auto_calculate_execution_guard": true
  },
  "timing": {
    "sleep_between_orders": 6,
    "sleep_between_cycles": 10,
    "retry_delay": 5
  },
  "risk_management": {
    "partial_close_ratio": 0.5,
    "add_position_ratio": 0.3,
    "add_collateral_ratio": 0.2,
    "stop_loss_percent": 0.10,
    "take_profit_percent": 0.15
  },
  "logging": {
    "level": "INFO",
    "log_file": "dexlyn_trading.log",
    "console_output": true
  }
}
```

### 2. network.json - Network Settings
```json
{
  "testnet": {
    "contract_address": "0xae38541466939b577823389765d966ba206b19be954fc87011fa10dc91e2fe0f",
    "collateral_token": "0x4f316ce2960250e7ac1206a07d07b2cbef3897d3cb8c12369d30c08ecd39c61c::tusdc_coin::TUSDC",
    "size_decimals": 6,
    "collateral_decimals": 6,
    "price_decimals": 10
  },
  "mainnet": {
    "contract_address": "0x215f242bec12c3d66b469668bc48b71e87fc1c7fd8e1764ac773423f0e2ba18b",
    "collateral_token": "0x9176f70f125199a3e3d5549ce795a8e906eed75901d535ded623802f15ae3637::cdp_multi::CASH",
    "size_decimals": 8,
    "collateral_decimals": 8,
    "price_decimals": 10
  }
}
```

### 3. wallets.json - Wallet Configuration
```json
{
  "primary": {
    "address": "0xYOUR_WALLET_ADDRESS",
    "profile": "your_profile_name",
    "description": "Primary trading wallet"
  },
  "secondary": {
    "address": "0xANOTHER_WALLET_ADDRESS",
    "profile": "another_profile",
    "description": "Secondary wallet for hedging"
  }
}
```

### 4. pairs.json - Trading Pairs
```json
{
  "ETH_USD": {
    "type_arg": "ETH_USD",
    "description": "Ethereum vs US Dollar",
    "available_testnet": true,
    "available_mainnet": true,
    "default_size_usd": 100.0,
    "default_collateral_usd": 50.0,
    "default_price": 3500.0,
    "min_size_usd": 10.0,
    "max_size_usd": 1000.0
  },
  "BTC_USD": {
    "type_arg": "BTC_USD",
    "description": "Bitcoin vs US Dollar",
    "available_testnet": true,
    "available_mainnet": true,
    "default_size_usd": 100.0,
    "default_collateral_usd": 50.0,
    "default_price": 50000.0,
    "min_size_usd": 10.0,
    "max_size_usd": 1000.0
  }
}
```

## 📊 Order Field Reference

### Core Required Fields
| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `name` | string | ✅ | Order name for logging | `"Open ETH Long"` |
| `action` | string | ✅ | Order action type | `"market_open_long"` |
| `pair` | string | ✅ | Trading pair | `"ETH_USD"` |
| `wallet` | string | ✅ | Wallet to use | `"primary"` |

### Size and Collateral Fields
| Field | Type | Description | Testnet Example | Mainnet Example |
|-------|------|-------------|-----------------|-----------------|
| `size_usd` | number | Position size in USD | `100.0` ($100) | `100.0` ($100) |
| `size_units` | integer | Exact size in units | `100000000` | `10000000000` |
| `collateral_usd` | number | Collateral in USD | `50.0` ($50) | `50.0` ($50) |
| `collateral_units` | integer | Exact collateral in units | `50000000` | `5000000000` |

### Price Fields
| Field | Type | Description | Example Value |
|-------|------|-------------|---------------|
| `price` | number | Price in USD | `3500.0` |
| `price_units` | integer | Exact price in units | `3500000000000000` |
| `stop_loss` | number | Stop loss in USD | `3150.0` |
| `stop_loss_units` | integer | Exact stop loss in units | `3150000000000000` |
| `take_profit` | number | Take profit in USD | `3850.0` |
| `take_profit_units` | integer | Exact take profit in units | `3850000000000000` |

### Boolean Flags
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `is_long` | boolean | auto | `true` for LONG, `false` for SHORT |
| `is_increase` | boolean | auto | `true` to open/add, `false` to close |
| `is_market` | boolean | auto | `true` for market, `false` for limit |
| `can_execute_above_price` | boolean | auto | Execution guard for slippage |

### Advanced Fields
| Field | Type | Description |
|-------|------|-------------|
| `custom_parameters` | object | Raw parameters for complete control |
| `wait_before` | number | Seconds to wait before execution |
| `description` | string | Order description for reference |

## 🎯 Trading Strategies

### Pre-built Strategies

#### 1. Basic Cycle
```json
{
  "basic_cycle": {
    "name": "Basic ETH Open/Close Cycle",
    "description": "Simple cycle opening and closing both LONG and SHORT positions",
    "network": "testnet",
    "cycles": -1,
    "orders": [
      {
        "name": "Open LONG ETH",
        "action": "market_open_long",
        "pair": "ETH_USD",
        "wallet": "primary",
        "size_usd": 100.0,
        "collateral_usd": 50.0,
        "price": 3500.0
      },
      {
        "name": "Open SHORT ETH",
        "action": "market_open_short",
        "pair": "ETH_USD",
        "wallet": "secondary", 
        "size_usd": 100.0,
        "collateral_usd": 50.0,
        "price": 3500.0
      }
    ]
  }
}
```

#### 2. Advanced Position Management
```json
{
  "advanced_mgmt": {
    "name": "Advanced Position Management",
    "description": "Open, add to position, partial close, full close",
    "network": "testnet",
    "cycles": 1,
    "orders": [
      {
        "name": "Open Position",
        "action": "market_open_long",
        "pair": "ETH_USD",
        "wallet": "primary",
        "size_usd": 100.0,
        "collateral_usd": 50.0
      },
      {
        "name": "Add to Position",
        "action": "add_to_position",
        "pair": "ETH_USD",
        "wallet": "primary",
        "size_usd": 30.0,
        "additional_collateral_usd": 15.0
      },
      {
        "name": "Partial Close",
        "action": "partial_close",
        "pair": "ETH_USD",
        "wallet": "primary",
        "close_percent": 0.5,
        "current_position_size_usd": 130.0
      }
    ]
  }
}
```

### Creating Custom Strategies

#### Simple USD-Based Strategy
```json
{
  "my_simple_strategy": {
    "name": "My Simple Strategy",
    "network": "testnet",
    "cycles": 5,
    "orders": [
      {
        "name": "Buy ETH",
        "action": "market_open_long",
        "pair": "ETH_USD",
        "wallet": "primary",
        "size_usd": 75.0,
        "collateral_usd": 37.5,
        "price": 3525.0,
        "stop_loss": 3172.5,
        "take_profit": 3877.5
      },
      {
        "name": "Sell ETH",
        "action": "market_close_long",
        "pair": "ETH_USD", 
        "wallet": "primary",
        "size_usd": 75.0,
        "price": 3600.0
      }
    ]
  }
}
```

#### Advanced Units-Based Strategy
```json
{
  "my_advanced_strategy": {
    "name": "Precision Trading",
    "network": "mainnet",
    "cycles": 3,
    "orders": [
      {
        "name": "Precision BTC Long",
        "action": "limit_open_long",
        "pair": "BTC_USD",
        "wallet": "primary",
        "size_units": 7500000000,
        "collateral_units": 3750000000,
        "price_units": 500000000000000,
        "stop_loss_units": 450000000000000,
        "take_profit_units": 550000000000000,
        "description": "Precision BTC long with exact units"
      }
    ]
  }
}
```

#### Complete Custom Control Strategy
```json
{
  "full_control_strategy": {
    "name": "Full Parameter Control",
    "network": "testnet",
    "cycles": 1,
    "orders": [
      {
        "name": "Custom ETH Order",
        "action": "custom",
        "pair": "ETH_USD",
        "wallet": "primary",
        "custom_parameters": {
          "size_units": 100000000,
          "collateral_units": 50000000,
          "price_units": 3500000000000000,
          "is_long": true,
          "is_increase": true,
          "is_market": true,
          "stop_loss_units": 3150000000000000,
          "take_profit_units": 3850000000000000,
          "can_execute_above_price": false
        }
      }
    ]
  }
}
```

## ⚙️ Advanced Features

### Order Actions Reference

| Action | Description | Auto Parameters |
|--------|-------------|-----------------|
| `market_open_long` | Open LONG with market order | `is_long=true, is_increase=true, is_market=true` |
| `market_open_short` | Open SHORT with market order | `is_long=false, is_increase=true, is_market=true` |
| `limit_open_long` | Open LONG with limit order | `is_long=true, is_increase=true, is_market=false` |
| `limit_open_short` | Open SHORT with limit order | `is_long=false, is_increase=true, is_market=false` |
| `market_close_long` | Close LONG with market order | `is_long=true, is_increase=false, is_market=true` |
| `market_close_short` | Close SHORT with market order | `is_long=false, is_increase=false, is_market=true` |
| `limit_close_long` | Close LONG with limit order | `is_long=true, is_increase=false, is_market=false` |
| `limit_close_short` | Close SHORT with limit order | `is_long=false, is_increase=false, is_market=false` |
| `add_to_position` | Add to existing position | `is_increase=true` |
| `add_collateral` | Add collateral only | `size=0, is_increase=true` |
| `partial_close` | Partial close position | `is_increase=false` |
| `full_close` | Full close position | `is_increase=false` |
| `custom` | Complete custom control | No auto parameters |

### Execution Guard Logic

The `can_execute_above_price` parameter is automatically calculated for optimal execution:

| Trade Type | is_long | is_increase | Optimal Setting | Reasoning |
|------------|---------|-------------|-----------------|-----------|
| Open Long | true | true | false | Buy at or below target price |
| Open Short | false | true | true | Sell at or above target price |
| Close Long | true | false | true | Sell at or above target price |
| Close Short | false | false | false | Buy at or below target price |

### Units Conversion Guide

**Testnet:**
- Size: 1 USD = 1,000,000 units
- Collateral: 1 USD = 1,000,000 units  
- Price: 1 USD = 10,000,000,000 units

**Mainnet:**
- Size: 1 USD = 100,000,000 units
- Collateral: 1 USD = 100,000,000 units
- Price: 1 USD = 10,000,000,000 units

**Examples:**
```json
// Testnet - $100 position
"size_usd": 100.0        // Auto-converted to 100000000 units
"size_units": 100000000  // Explicit units

// Mainnet - $100 position  
"size_usd": 100.0        // Auto-converted to 10000000000 units
"size_units": 10000000000 // Explicit units

// Price - $3500
"price": 3500.0          // Auto-converted to 3500000000000000 units
"price_units": 3500000000000000 // Explicit units
```

## 🛠️ Command Line Usage

### Basic Commands
```bash
# Generate all configuration files
python dexlyn_bot.py --generate-configs

# Generate field reference
python dexlyn_bot.py --generate-reference

# Run basic strategy
python dexlyn_bot.py --strategy basic_cycle

# Run with limited cycles
python dexlyn_bot.py --strategy basic_cycle --cycles 3

# Use custom config directory
python dexlyn_bot.py --config-dir ./my_configs
```

### Advanced Usage Examples

```bash
# Multiple wallets strategy
python dexlyn_bot.py --strategy multi_wallet --cycles 5

# Quick test with single order
python dexlyn_bot.py --custom-config quick_test.json --cycles 1
```


## 📋 Test Execution Commands

### Individual Test Categories
```bash
# Use the main bot with custom strategy file
python dexlyn_bot.py --strategy-file test_cases/basic_orders/basic_market_orders.json

# Run test suite
python run_all_tests.py --suite basic_market_orders

# List all available tests
python run_all_tests.py --list
```

## 🎯 Test Coverage Summary

### Order Types Covered:
- ✅ Market Open Long/Short
- ✅ Limit Open Long/Short  
- ✅ Market Close Long/Short
- ✅ Limit Close Long/Short
- ✅ Add to Position
- ✅ Add Collateral
- ✅ Partial Close
- ✅ Full Close
- ✅ Custom Orders

### Position Flows Covered:
- ✅ Complete Long Lifecycle
- ✅ Complete Short Lifecycle  
- ✅ Hedging Strategies
- ✅ Multi-Pair Trading
- ✅ Portfolio Distribution
- ✅ Scalping Strategies
- ✅ Recovery Strategies

### Risk Management Covered:
- ✅ Stop Loss Configurations
- ✅ Take Profit Configurations
- ✅ Position Sizing Variations
- ✅ Leverage Management
- ✅ Multi-Wallet Risk Distribution

### Advanced Scenarios:
- ✅ Units-Based Precision Trading
- ✅ High Frequency Ordering
- ✅ Large Position Testing
- ✅ Multi-Cycle Strategies
- ✅ Custom Parameter Control

## 🔧 Troubleshooting

### Common Issues

**1. Password Not Set**
```
Error: Please set your password: export SUPRA_CLI_PASSWORD='your#password'
```
Solution: Set the environment variable with your actual password.

**2. Module Not Found**
```
ModuleNotFoundError: No module named 'pexpect'
```
Solution: Install dependencies:
```bash
pip install pexpect wexpect python-dotenv
```



### Log Files

- `dexlyn_trading.log` - Main trading log

## 📋 Best Practices

### Risk Management
1. **Start Small**: Begin with testnet and small position sizes
2. **Use Stop Losses**: Always set stop losses for protection
3. **Manage Leverage**: Avoid excessive leverage (5-10x recommended)
4. **Position Sizing**: Don't risk more than 2-5% per trade
5. **Diversify**: Use multiple pairs and strategies

### Configuration Tips
1. **Backup Configs**: Keep backups of working configurations
2. **Version Control**: Use git to track configuration changes
3. **Incremental Testing**: Test strategies with small cycles first
4. **Monitor Logs**: Regularly check log files for errors
5. **Update Regularly**: Keep the bot and configurations updated

### Performance Optimization
1. **Adjust Timing**: Increase sleep times during high volatility
2. **Network Selection**: Use testnet for strategy development
3. **Order Types**: Use limit orders during normal market conditions
4. **Execution Guards**: Always use execution guards for slippage protection

## 🆘 Support

### Getting Help
1. Check the log files for error details
2. Verify all configuration files are properly formatted
3. Ensure your Supra CLI is working independently
4. Test with the basic cycle strategy first

### Emergency Stop
To immediately stop the bot:
- Press `Ctrl+C` in the terminal
- The bot will complete the current order and stop gracefully

### Recovery
If the bot stops unexpectedly:
1. Check the last completed order in logs
2. Verify wallet balances
3. Check open positions on Dexlyn
4. Resume with adjusted strategy if needed

---

## 📞 Need More Help?

If you encounter issues not covered in this documentation:
1. Check the `field_reference.json` for complete field documentation
2. Review the example strategies in `strategies.json`
3. Test with the basic cycle strategy to verify setup
4. Ensure your Supra CLI configuration is correct

Happy trading! 🎯