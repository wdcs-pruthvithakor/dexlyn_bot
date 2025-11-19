#!/usr/bin/env python3
"""
🎯 DEXLYN PERPETUALS BOT - FULLY CUSTOMIZABLE ORDERS

A completely customizable trading bot where EVERY order parameter can be set via JSON configuration.
Users can specify any field for each order with complete flexibility.

📁 CONFIGURATION FILES:
- config.json          → Main trading configuration
- network.json         → Network and contract settings  
- wallets.json         → Wallet addresses and profiles
- strategies.json      → Trading strategies and cycles
- pairs.json           → Trading pairs and defaults

🎯 KEY FEATURES:
✅ Every order field customizable via JSON
✅ Smart defaults with manual override
✅ Support for all place_order_v3 parameters
✅ Flexible order definitions
✅ Validation and error handling
✅ Customizable Supra CLI command
"""

import os
import sys
import time
import json
import shlex
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import dotenv

dotenv.load_dotenv()

# ========== DEFAULT CONFIGURATION PATHS ==========

CONFIG_PATHS = {
    "main": "config.json",
    "network": "network.json", 
    "wallets": "wallets.json",
    "strategies": "strategies.json",
    "pairs": "pairs.json"
}

RPC_URLS = {
    "testnet": "https://rpc-testnet.supra.com",
    "mainnet": "https://rpc-mainnet.supra.com"
}

# ========== COMPLETE ORDER FIELD DEFINITIONS ==========

# All available fields for place_order_v3 with descriptions and defaults
COMPLETE_ORDER_FIELDS = {
    # Required core fields
    "action": {
        "type": "string",
        "required": True,
        "description": "Order action type",
        "options": [
            "market_open_long", "market_open_short", "limit_open_long", "limit_open_short",
            "market_close_long", "market_close_short", "limit_close_long", "limit_close_short",
            "add_to_position", "add_collateral", "partial_close", "full_close",
            "custom"  # For fully custom parameter specification
        ]
    },
    
    # Identification fields
    "name": {
        "type": "string", 
        "required": True,
        "description": "Order name for logging"
    },
    "pair": {
        "type": "string",
        "required": True,
        "description": "Trading pair from pairs.json"
    },
    "wallet": {
        "type": "string",
        "required": True,
        "description": "Wallet from wallets.json"
    },
    
    # Core order parameters (can be specified in USD or units)
    "size_usd": {
        "type": "number",
        "required": False,
        "description": "Position size in USD (auto-converted to units)",
        "default": 300.0
    },
    "size_units": {
        "type": "integer", 
        "required": False,
        "description": "Position size in blockchain units (overrides size_usd)"
    },
    "collateral_usd": {
        "type": "number",
        "required": False,
        "description": "Collateral in USD (auto-converted to units)",
        "default": 3.0
    },
    "collateral_units": {
        "type": "integer",
        "required": False, 
        "description": "Collateral in blockchain units (overrides collateral_usd)"
    },
    "price": {
        "type": "number",
        "required": False,
        "description": "Price in USD (auto-converted to units)",
        "default": 3500.0
    },
    "price_units": {
        "type": "integer",
        "required": False,
        "description": "Price in blockchain units (overrides price)"
    },
    
    # Boolean flags (all optional with smart defaults)
    "is_long": {
        "type": "boolean",
        "required": False,
        "description": "True for LONG, False for SHORT (auto-determined from action)"
    },
    "is_increase": {
        "type": "boolean", 
        "required": False,
        "description": "True to open/add, False to close/reduce (auto-determined from action)"
    },
    "is_market": {
        "type": "boolean",
        "required": False,
        "description": "True for market order, False for limit order (auto-determined from action)"
    },
    "can_execute_above_price": {
        "type": "boolean",
        "required": False,
        "description": "Execution guard (auto-calculated for optimal execution)"
    },
    
    # Risk management fields
    "stop_loss": {
        "type": "number",
        "required": False,
        "description": "Stop loss price in USD",
        "default": 0.0
    },
    "stop_loss_units": {
        "type": "integer",
        "required": False,
        "description": "Stop loss in units (overrides stop_loss)"
    },
    "take_profit": {
        "type": "number", 
        "required": False,
        "description": "Take profit price in USD",
        "default": 0.0
    },
    "take_profit_units": {
        "type": "integer",
        "required": False,
        "description": "Take profit in units (overrides take_profit)"
    },
    
    # Advanced parameters
    "reduce_only": {
        "type": "boolean",
        "required": False,
        "description": "Reduce only flag",
        "default": False
    },
    "post_only": {
        "type": "boolean",
        "required": False, 
        "description": "Post only flag",
        "default": False
    },
    
    # Custom raw parameters (for advanced users)
    "custom_parameters": {
        "type": "object",
        "required": False,
        "description": "Raw parameters for complete control (overrides all other fields)"
    },
    
    # Order metadata
    "description": {
        "type": "string",
        "required": False,
        "description": "Order description for reference"
    },
    "wait_before": {
        "type": "number",
        "required": False,
        "description": "Seconds to wait before executing this order",
        "default": 0
    },
    "condition": {
        "type": "object",
        "required": False,
        "description": "Execution conditions (future feature)"
    }
}

# ========== DEFAULT CONFIGURATIONS ==========

DEFAULT_CONFIG = {
    "network": "testnet",
    "default_strategy": "basic_cycle",
    "supra_command": "supra",
    "trading": {
        "default_size_usd": 300.0,
        "default_collateral_usd": 3.0,
        "default_leverage": 5.0,
        "max_position_size_usd": 500000.0,
        "min_position_size_usd": 300.0
    },
    "orders": {
        "default_slippage_tolerance": 0.01,
        "default_timeout_seconds": 240,
        "confirmation_attempts": 3,
        "auto_calculate_execution_guard": True
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
        "console_output": True
    }
}

DEFAULT_NETWORK = {
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

DEFAULT_WALLETS = {
    "trader_1": {
        "address": "0xyourownaddresshere",
        "profile": "your_profile_name",
        "description": "Primary trading wallet"
    },
    "trader_2": {
        "address": "yourownaddresshere",
        "profile": "your_profile_name",
        "description": "Secondary trading wallet"
    }
}

DEFAULT_PAIRS = {
    "ETH_USD": {
        "type_arg": "ETH_USD",
        "description": "Ethereum vs US Dollar",
        "available_testnet": True,
        "available_mainnet": True,
        "default_size_usd": 300.0,
        "default_collateral_usd": 3.0,
        "default_price": 3500.0,
        "min_size_usd": 300.0,
        "max_size_usd": 500000.0
    },
    "BTC_USD": {
        "type_arg": "BTC_USD",
        "description": "Bitcoin vs US Dollar",
        "available_testnet": True,
        "available_mainnet": True,
        "default_size_usd": 300.0,
        "default_collateral_usd": 3.0,
        "default_price": 50000.0,
        "min_size_usd": 300.0,
        "max_size_usd": 500000.0
    }
}

DEFAULT_STRATEGIES = {
    "basic_cycle": {
        "name": "Basic ETH Open/Close Cycle",
        "description": "Simple cycle opening and closing both LONG and SHORT positions",
        "network": "testnet",
        "cycles": -1,
        "orders": [
            {
                "name": "Open LONG ETH - Market",
                "action": "market_open_long",
                "pair": "ETH_USD",
                "wallet": "trader_1",
                "size_usd": 300.0,
                "collateral_usd": 3.0,
                "price": 3500.0,
                "stop_loss": 3150.0,
                "take_profit": 3850.0,
                "description": "Open long position with market order"
            },
            {
                "name": "Open SHORT ETH - Market", 
                "action": "market_open_short",
                "pair": "ETH_USD",
                "wallet": "trader_2",
                "size_usd": 300.0,
                "collateral_usd": 3.0,
                "price": 3500.0,
                "stop_loss": 3850.0,
                "take_profit": 3150.0,
                "description": "Open short position with market order"
            }
        ]
    },
    "fully_custom": {
        "name": "Fully Custom Orders Example",
        "description": "Demonstrates complete customization of all order fields",
        "network": "testnet", 
        "cycles": 1,
        "orders": [
            {
                "name": "Custom Limit Long",
                "action": "custom",
                "pair": "ETH_USD",
                "wallet": "trader_1",
                "custom_parameters": {
                    "size_units": 500000000,
                    "collateral_units": 10000000, 
                    "price_units": 3550000000000000,
                    "is_long": True,
                    "is_increase": True,
                    "is_market": False,
                    "stop_loss_units": 3195000000000000,
                    "take_profit_units": 3905000000000000,
                    "can_execute_above_price": False
                },
                "description": "Completely custom limit long order with all fields specified in units"
            }
        ]
    }
}

# ========== CONFIGURATION MANAGER ==========

class ConfigManager:
    """Manage all configuration loading and validation"""
    
    def __init__(self, config_dir: str = "."):
        self.config_dir = Path(config_dir)
        self.configs = {}
        
    def load_all_configs(self, custom_config_path: str = None) -> Dict[str, Any]:
        """Load all configuration files"""
        if custom_config_path:
            main_config = self.load_json_config(custom_config_path)
        else:
            main_config = self.load_json_config(CONFIG_PATHS["main"], DEFAULT_CONFIG)

        self.configs = {
            "main": main_config,
            "network": self.load_json_config(CONFIG_PATHS["network"], DEFAULT_NETWORK),
            "wallets": self.load_json_config(CONFIG_PATHS["wallets"], DEFAULT_WALLETS),
            "pairs": self.load_json_config(CONFIG_PATHS["pairs"], DEFAULT_PAIRS),
            "strategies": self.load_json_config(CONFIG_PATHS["strategies"], DEFAULT_STRATEGIES)
        }
        
        self.validate_configs()
        return self.configs
    
    def load_json_config(self, file_path: str, default_config: Dict = None) -> Dict:
        """Load JSON config file or return default if not exists"""
        path = self.config_dir / file_path
        
        if path.exists():
            try:
                with open(path, 'r') as f:
                    config = json.load(f)
                logging.info(f"✅ Loaded config: {file_path}")
                return config
            except Exception as e:
                logging.warning(f"⚠️ Failed to load {file_path}: {e}, using defaults")
        
        if default_config is not None:
            self.create_default_config(path, default_config)
            return default_config.copy()
        else:
            return {}
    
    def create_default_config(self, path: Path, default_config: Dict):
        """Create default config file for user to edit"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logging.info(f"📝 Created default config: {path}")
        except Exception as e:
            logging.error(f"❌ Failed to create default config {path}: {e}")
    
    def validate_configs(self):
        """Validate all loaded configurations"""
        network = self.configs["main"]["network"]
        if network not in self.configs["network"]:
            raise ValueError(f"Network '{network}' not found in network configuration")
        
        strategy = self.configs["main"]["default_strategy"]
        if strategy not in self.configs["strategies"]:
            raise ValueError(f"Strategy '{strategy}' not found in strategies configuration")
    
    def get_network_config(self, network: str = None) -> Dict:
        """Get network-specific configuration"""
        if network is None:
            network = self.configs["main"]["network"]
        return self.configs["network"][network]
    
    def get_strategy(self, strategy_name: str = None) -> Dict:
        """Get strategy configuration"""
        if strategy_name is None:
            strategy_name = self.configs["main"]["default_strategy"]
        return self.configs["strategies"][strategy_name]
    
    def get_wallet(self, wallet_name: str) -> Dict:
        """Get wallet configuration"""
        return self.configs["wallets"][wallet_name]
    
    def get_pair(self, pair_name: str) -> Dict:
        """Get trading pair configuration"""
        return self.configs["pairs"][pair_name]
    
    def get_supra_command(self) -> str:
        """Get the Supra CLI command from config"""
        return self.configs["main"].get("supra_command", "supra")

# ========== ADVANCED TRADING ENGINE ==========

class AdvancedTradingEngine:
    """Trading engine with complete order field customization"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.network = config_manager.configs["main"]["network"]
        self.network_config = config_manager.get_network_config()
        self.supra_command = config_manager.get_supra_command()
        self.function_id = f"{self.network_config['contract_address']}::managed_trading::place_order_v3"
        
    def usd_to_units(self, usd_amount: float, decimal_type: str = "size") -> int:
        """Convert USD amount to blockchain units"""
        decimals = self.network_config[f"{decimal_type}_decimals"]
        return int(usd_amount * (10 ** decimals))
    
    def price_to_units(self, price: float) -> int:
        """Convert price to blockchain units"""
        return int(price * (10 ** self.network_config["price_decimals"]))
    
    def create_order_parameters(self, order_config: Dict) -> List[str]:
        """Create order parameters with complete field customization"""
        
        # If custom_parameters is provided, use them directly
        if "custom_parameters" in order_config:
            return self.create_custom_order(order_config)
        
        # Otherwise, build parameters from individual fields
        return self.create_standard_order(order_config)
    
    def create_custom_order(self, order_config: Dict) -> List[str]:
        """Create order using completely custom parameters"""
        custom_params = order_config["custom_parameters"]
        wallet = self.config_manager.get_wallet(order_config["wallet"])
        
        # Validate required custom parameters
        required_fields = ["size_units", "collateral_units", "price_units", 
                          "is_long", "is_increase", "is_market", "can_execute_above_price"]
        
        for field in required_fields:
            if field not in custom_params:
                raise ValueError(f"Custom order missing required field: {field}")
        
        logging.info(f"🎯 Creating CUSTOM order: {order_config['name']}")
        
        return [
            f"address:{wallet['address']}",
            f"u64:{custom_params['size_units']}",
            f"u64:{custom_params['collateral_units']}",
            f"u64:{custom_params['price_units']}",
            f"bool:{str(custom_params['is_long']).lower()}",
            f"bool:{str(custom_params['is_increase']).lower()}",
            f"bool:{str(custom_params['is_market']).lower()}",
            f"u64:{custom_params.get('stop_loss_units', 0)}",
            f"u64:{custom_params.get('take_profit_units', 0)}",
            f"bool:{str(custom_params['can_execute_above_price']).lower()}",
            "address:0x0"
        ]
    
    def create_standard_order(self, order_config: Dict) -> List[str]:
        """Create order using standard field definitions"""
        
        # Get configuration
        pair_config = self.config_manager.get_pair(order_config["pair"])
        wallet = self.config_manager.get_wallet(order_config["wallet"])
        
        # Convert amounts to units (prefer explicit units over USD conversions)
        size_units = self.get_size_units(order_config, pair_config)
        collateral_units = self.get_collateral_units(order_config, pair_config)
        price_units = self.get_price_units(order_config, pair_config)
        stop_loss_units = self.get_stop_loss_units(order_config)
        take_profit_units = self.get_take_profit_units(order_config)
        
        # Determine order type parameters
        action = order_config["action"]
        is_long, is_increase, is_market = self.parse_action_flags(action, order_config)
        
        # Calculate execution guard (can be overridden)
        auto_calculate = self.config_manager.configs["main"]["orders"]["auto_calculate_execution_guard"]
        if "can_execute_above_price" in order_config:
            can_execute_above = order_config["can_execute_above_price"]
        elif auto_calculate:
            can_execute_above = self.calculate_execution_guard(is_long, is_increase, is_market)
        else:
            can_execute_above = True  # Default safe value
        
        logging.info(f"📊 Creating order: {order_config['name']}")
        logging.info(f"   Size: {size_units} units")
        logging.info(f"   Collateral: {collateral_units} units")
        logging.info(f"   Price: {price_units} units")
        logging.info(f"   Execution: Long={is_long}, Increase={is_increase}, Market={is_market}")
        logging.info(f"   Guard: can_execute_above_price={can_execute_above}")
        
        return [
            f"address:{wallet['address']}",
            f"u64:{size_units}",
            f"u64:{collateral_units}",
            f"u64:{price_units}",
            f"bool:{str(is_long).lower()}",
            f"bool:{str(is_increase).lower()}",
            f"bool:{str(is_market).lower()}",
            f"u64:{stop_loss_units}",
            f"u64:{take_profit_units}",
            f"bool:{str(can_execute_above).lower()}",
            "address:0x0"
        ]
    
    def get_size_units(self, order_config: Dict, pair_config: Dict) -> int:
        """Get size in units, preferring explicit units over USD conversion"""
        if "size_units" in order_config:
            return order_config["size_units"]
        elif "size_usd" in order_config:
            return self.usd_to_units(order_config["size_usd"], "size")
        else:
            return self.usd_to_units(pair_config["default_size_usd"], "size")
    
    def get_collateral_units(self, order_config: Dict, pair_config: Dict) -> int:
        """Get collateral in units"""
        if "collateral_units" in order_config:
            return order_config["collateral_units"]
        elif "collateral_usd" in order_config:
            return self.usd_to_units(order_config["collateral_usd"], "collateral")
        else:
            return self.usd_to_units(pair_config["default_collateral_usd"], "collateral")
    
    def get_price_units(self, order_config: Dict, pair_config: Dict) -> int:
        """Get price in units"""
        if "price_units" in order_config:
            return order_config["price_units"]
        elif "price" in order_config:
            return self.price_to_units(order_config["price"])
        else:
            return self.price_to_units(pair_config["default_price"])
    
    def get_stop_loss_units(self, order_config: Dict) -> int:
        """Get stop loss in units"""
        if "stop_loss_units" in order_config:
            return order_config["stop_loss_units"]
        elif "stop_loss" in order_config and order_config["stop_loss"] > 0:
            return self.price_to_units(order_config["stop_loss"])
        else:
            return 0
    
    def get_take_profit_units(self, order_config: Dict) -> int:
        """Get take profit in units"""
        if "take_profit_units" in order_config:
            return order_config["take_profit_units"]
        elif "take_profit" in order_config and order_config["take_profit"] > 0:
            return self.price_to_units(order_config["take_profit"])
        else:
            return 0
    
    def parse_action_flags(self, action: str, order_config: Dict) -> tuple:
        """Parse action and determine order flags with manual override support"""
        
        # Action type mappings
        action_map = {
            "market_open_long": (True, True, True),
            "market_open_short": (False, True, True),
            "limit_open_long": (True, True, False),
            "limit_open_short": (False, True, False),
            "market_close_long": (True, False, True),
            "market_close_short": (False, False, True),
            "limit_close_long": (True, False, False),
            "limit_close_short": (False, False, False),
            "add_to_position": (order_config.get("is_long", True), True, order_config.get("is_market", False)),
            "add_collateral": (order_config.get("is_long", True), True, True),
            "partial_close": (order_config.get("is_long", True), False, order_config.get("is_market", False)),
            "full_close": (order_config.get("is_long", True), False, order_config.get("is_market", True)),
            "custom": (order_config.get("is_long", True), order_config.get("is_increase", True), order_config.get("is_market", False))
        }
        
        if action not in action_map:
            raise ValueError(f"Unknown action: {action}")
        
        default_long, default_increase, default_market = action_map[action]
        
        # Allow manual override of any flag
        is_long = order_config.get("is_long", default_long)
        is_increase = order_config.get("is_increase", default_increase)
        is_market = order_config.get("is_market", default_market)
        
        return is_long, is_increase, is_market
    
    def calculate_execution_guard(self, is_long: bool, is_increase: bool, is_market: bool) -> bool:
        """Calculate optimal execution guard"""
        if is_increase and is_long:
            return False  # Buy at or below target
        elif is_increase and not is_long:
            return True   # Sell at or above target
        elif not is_increase and is_long:
            return True   # Sell at or above target
        else:  # not is_increase and not is_long
            return False  # Buy at or below target

# ========== TRADE EXECUTOR ==========

class AdvancedTradeExecutor:
    """Execute trades with complete field customization"""
    
    def __init__(self, config_manager: ConfigManager, engine: AdvancedTradingEngine):
        self.config_manager = config_manager
        self.engine = engine
        self.password = os.environ.get("SUPRA_CLI_PASSWORD", "")
        
    def execute_order(self, order_config: Dict) -> bool:
        """Execute a single order with complete customization"""
        try:
            # Platform detection
            if sys.platform.startswith("win"):
                import wexpect as expect
                logging.info("🪟 Detected Windows platform, using wexpect")
            else:
                import pexpect as expect
                logging.info("🖥️ Detected Unix-like platform, using pexpect")
            
            # Handle wait_before if specified
            wait_before = order_config.get("wait_before", 0)
            if wait_before > 0:
                logging.info(f"⏳ Waiting {wait_before} seconds before order...")
                time.sleep(wait_before)
            
            # Create order parameters
            order_params = self.engine.create_order_parameters(order_config)
            
            # Get wallet and pair info
            wallet = self.config_manager.get_wallet(order_config["wallet"])
            pair = self.config_manager.get_pair(order_config["pair"])
            network_config = self.engine.network_config
            
            # Build command with customizable Supra command
            supra_command = self.engine.supra_command
            cmd = [
                supra_command, "move", "tool", "run",
                "--function-id", self.engine.function_id,
                "--args", *order_params,
                "--type-args",
                f"{network_config['contract_address']}::pair_types::{pair['type_arg']}",
                network_config['collateral_token'],
                "--profile", wallet['profile'],
                "--rpc-url", RPC_URLS[self.engine.network]
            ]
            cmd_str = " ".join(shlex.quote(arg) for arg in cmd)
            logging.info(f"🤖 Executing: {order_config['name']}")
            logging.info(f"🤖 Executing: {order_config['name']}")
            logging.info(f"Full command: {cmd_str}")
            if order_config.get("description"):
                logging.info(f"📝 Description: {order_config['description']}")
            
            # Execute command
            child = expect.spawn(cmd_str, encoding='utf-8', timeout=self.config_manager.configs["main"]["orders"]["default_timeout_seconds"])
            child.delaybeforesend = 0.15
            logging.info("🚀 Command sent, awaiting response...")
            
            # Handle password and confirmations
            try:
                child.expect([r"[Pp]ass(word|phrase)", r"Enter your password", r"Profile passphrase"], timeout=10)
                child.sendline(self.password)
                child.sendline("\n")
            except:
                pass

            confirmation_attempts = self.config_manager.configs["main"]["orders"]["confirmation_attempts"]
            for _ in range(confirmation_attempts):
                try:
                    child.expect([r"\(Y/n\)", r"confirm", r"Press Enter", r"gas", r"fee"], timeout=2)
                    child.sendline('\n')
                except:
                    pass

            child.expect(expect.EOF, timeout=self.config_manager.configs["main"]["orders"]["default_timeout_seconds"])
            output = child.before or ""
            print("status code:", getattr(child, "exitstatus", 0))
            if "success" in output.lower() or "executed" in output.lower():
                logging.info(f"✅ {order_config['name']} - SUCCESS")
                return True
            else:
                logging.info(f"📄 Output: {output[:3000]}...")
                return True
                
        except Exception as e:
            logging.error(f"❌ {order_config['name']} - FAILED: {e}")
            return False
        finally:
            try:
                child.close(force=True)
            except Exception:
                pass
    
    def execute_strategy(self, strategy_name: str = None) -> bool:
        """Execute a complete trading strategy"""
        strategy = self.config_manager.get_strategy(strategy_name)
        orders = strategy.get("orders", [])
        
        logging.info(f"🔄 Executing strategy: {strategy['name']}")
        logging.info(f"📝 Description: {strategy['description']}")
        logging.info(f"🔧 Using Supra command: {self.engine.supra_command}")
        
        success_count = 0
        for i, order in enumerate(orders, 1):
            logging.info(f"📊 [{i}/{len(orders)}] Processing: {order['name']}")
            
            success = self.execute_order(order)
            if success:
                success_count += 1
            
            # Sleep between orders (except last one)
            if i < len(orders):
                sleep_time = self.config_manager.configs["main"]["timing"]["sleep_between_orders"]
                logging.info(f"⏳ Waiting {sleep_time} seconds...")
                time.sleep(sleep_time)
        
        logging.info(f"🎯 Strategy completed: {success_count}/{len(orders)} orders successful")
        return success_count == len(orders)

# ========== CONFIGURATION GENERATORS ==========

def generate_complete_config_files():
    """Generate all configuration files with complete examples"""
    
    # Enhanced strategies with complete field examples
    enhanced_strategies = {
        **DEFAULT_STRATEGIES,
        "complete_examples": {
            "name": "Complete Field Examples",
            "description": "Shows all possible field customizations",
            "network": "testnet",
            "cycles": 1,
            "orders": [
                {
                    "name": "USD-Based Market Long",
                    "action": "market_open_long",
                    "pair": "ETH_USD",
                    "wallet": "trader_1",
                    "size_usd": 150.0,
                    "collateral_usd": 75.0,
                    "price": 3550.0,
                    "stop_loss": 3195.0,
                    "take_profit": 3905.0,
                    "description": "Using USD amounts (auto-converted to units)"
                },
                {
                    "name": "Units-Based Limit Short", 
                    "action": "limit_open_short",
                    "pair": "ETH_USD",
                    "wallet": "trader_2",
                    "size_units": 75000000,
                    "collateral_units": 37500000,
                    "price_units": 3600000000000000,
                    "stop_loss_units": 3960000000000000,
                    "take_profit_units": 3240000000000000,
                    "description": "Using exact blockchain units"
                },
                {
                    "name": "Manual Flags Override",
                    "action": "add_to_position",
                    "pair": "ETH_USD", 
                    "wallet": "trader_1",
                    "size_usd": 50.0,
                    "is_long": False,  # Override default
                    "is_market": True, # Override default  
                    "can_execute_above_price": True,  # Manual execution guard
                    "description": "Manually overriding auto-calculated flags"
                },
                {
                    "name": "Fully Custom Raw Order",
                    "action": "custom",
                    "pair": "ETH_USD",
                    "wallet": "trader_1", 
                    "custom_parameters": {
                        "size_units": 200000000,
                        "collateral_units": 100000000,
                        "price_units": 3650000000000000,
                        "is_long": True,
                        "is_increase": True, 
                        "is_market": False,
                        "stop_loss_units": 3285000000000000,
                        "take_profit_units": 4015000000000000,
                        "can_execute_above_price": False
                    },
                    "description": "Complete control with raw parameters"
                },
                {
                    "name": "Delayed Order Execution",
                    "action": "market_close_long", 
                    "pair": "ETH_USD",
                    "wallet": "trader_1",
                    "size_usd": 150.0,
                    "wait_before": 10,
                    "description": "Waits 10 seconds before executing"
                }
            ]
        }
    }
    
    configs = {
        "config.json": DEFAULT_CONFIG,
        "network.json": DEFAULT_NETWORK,
        "wallets.json": DEFAULT_WALLETS,
        "pairs.json": DEFAULT_PAIRS,
        "strategies.json": enhanced_strategies
    }
    
    for filename, config in configs.items():
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Generated {filename}")
    
    # Generate field reference
    generate_field_reference()

def generate_field_reference():
    """Generate a reference file showing all available order fields"""
    reference = {
        "order_field_reference": COMPLETE_ORDER_FIELDS,
        "examples": {
            "simple_usd_based_order": {
                "name": "Simple USD-Based Order",
                "action": "market_open_long", 
                "pair": "ETH_USD",
                "wallet": "trader_1",
                "size_usd": 100.0,
                "collateral_usd": 50.0,
                "price": 3500.0
            },
            "advanced_units_based_order": {
                "name": "Advanced Units-Based Order",
                "action": "limit_open_short",
                "pair": "ETH_USD",
                "wallet": "trader_2", 
                "size_units": 50000000,
                "collateral_units": 25000000,
                "price_units": 3600000000000000,
                "stop_loss_units": 3960000000000000,
                "take_profit_units": 3240000000000000,
                "is_long": False,
                "is_increase": True,
                "is_market": False,
                "can_execute_above_price": True
            },
            "completely_custom_order": {
                "name": "Completely Custom Order",
                "action": "custom",
                "pair": "ETH_USD",
                "wallet": "trader_1",
                "custom_parameters": {
                    "size_units": 100000000,
                    "collateral_units": 50000000,
                    "price_units": 3500000000000000,
                    "is_long": True,
                    "is_increase": True,
                    "is_market": True,
                    "stop_loss_units": 3150000000000000,
                    "take_profit_units": 3850000000000000,
                    "can_execute_above_price": False
                }
            }
        }
    }
    
    with open("field_reference.json", 'w') as f:
        json.dump(reference, f, indent=2)
    print("✅ Generated field_reference.json")

# ========== MAIN BOT CONTROLLER ==========

class AdvancedDexlynTradingBot:
    """Main trading bot controller with complete customization"""
    
    def __init__(self, config_dir: str = "."):
        self.config_manager = ConfigManager(config_dir)
        self.configs = self.config_manager.load_all_configs()
        self.engine = AdvancedTradingEngine(self.config_manager)
        self.executor = AdvancedTradeExecutor(self.config_manager, self.engine)
    
    def run(self, strategy_name: str = None, cycles: int = None):
        """Run the trading bot"""
        if strategy_name is None:
            strategy_name = self.configs["main"]["default_strategy"]
        
        strategy = self.config_manager.get_strategy(strategy_name)
        if cycles is None:
            cycles = strategy.get("cycles", -1)
        
        logging.info("🚀 DEXLYN ADVANCED TRADING BOT STARTING")
        logging.info(f"🌐 Network: {self.configs['main']['network']}")
        logging.info(f"📈 Strategy: {strategy['name']}")
        logging.info(f"🔧 Supra Command: {self.engine.supra_command}")
        logging.info(f"🔁 Cycles: {'Infinite' if cycles == -1 else cycles}")
        logging.info(f"📊 Orders in strategy: {len(strategy.get('orders', []))}")
        
        cycle_count = 0
        try:
            while cycles == -1 or cycle_count < cycles:
                cycle_count += 1
                logging.info(f"\n🎯 CYCLE #{cycle_count}")
                
                success = self.executor.execute_strategy(strategy_name)
                
                if cycles == -1 or cycle_count < cycles:
                    sleep_time = self.configs["main"]["timing"]["sleep_between_cycles"]
                    logging.info(f"😴 Sleeping {sleep_time} seconds...")
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            logging.info("\n🛑 Trading bot stopped by user")
        except Exception as e:
            logging.error(f"💥 Unexpected error: {e}")

# ========== MAIN ENTRY ==========

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Dexlyn Perpetuals Trading Bot - Complete Field Customization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
🎯 COMPLETE FIELD CUSTOMIZATION GUIDE:

ORDER FIELDS - YOU CAN CUSTOMIZE EVERYTHING:

Basic Fields (Auto-converted):
  size_usd: 100.0           → Position size in USD
  collateral_usd: 50.0       → Collateral in USD  
  price: 3500.0              → Price in USD
  stop_loss: 3150.0          → Stop loss in USD
  take_profit: 3850.0        → Take profit in USD

Advanced Fields (Exact units):
  size_units: 50000000       → Exact size in blockchain units
  collateral_units: 25000000 → Exact collateral in units
  price_units: 3500000000000000 → Exact price in units
  stop_loss_units: 3150000000000000 → Exact stop loss in units

Boolean Flags (Manual override):
  is_long: true/false        → LONG/SHORT position
  is_increase: true/false    → Open/Close position  
  is_market: true/false      → Market/Limit order
  can_execute_above_price: true/false → Execution guard

Complete Control:
  custom_parameters:         → Raw parameters for full control
    "size_units": 100000000,
    "collateral_units": 50000000, 
    "price_units": 3500000000000000,
    "is_long": true,
    "is_increase": true,
    "is_market": true,
    "can_execute_above_price": false

CUSTOMIZABLE SUPRA COMMAND:
  supra_command: "supra"     → Change to "supra_new", "supra-cli", or custom path

QUICK START:
1. Generate configs: python {sys.argv[0]} --generate-configs
2. Edit wallets.json with your addresses
3. Edit config.json to change supra_command if needed
4. Set password: export SUPRA_CLI_PASSWORD='your#password'
5. Run: python {sys.argv[0]} --strategy complete_examples

EXAMPLES:
  
  Simple USD-based trading:
    python {sys.argv[0]} --strategy basic_cycle

  Advanced units-based trading:
    python {sys.argv[0]} --strategy complete_examples

  Custom strategy file:
    python {sys.argv[0]} --custom-config my_strategy.json

  Custom Supra command:
    Edit config.json: "supra_command": "supra_new"
        """
    )
    
    parser.add_argument("--generate-configs", action="store_true", help="Generate all configuration files with examples")
    parser.add_argument("--generate-reference", action="store_true", help="Generate field reference file")
    parser.add_argument("--strategy", help="Strategy name to execute")
    parser.add_argument("--cycles", type=int, help="Number of cycles to run")
    parser.add_argument("--config-dir", default=".", help="Configuration directory")
    parser.add_argument("--custom-config", help="Custom strategy JSON file")
    
    args = parser.parse_args()
    
    # Setup logging
    log_config = DEFAULT_CONFIG.get("logging", {})
    log_config = ConfigManager(args.config_dir).load_json_config(CONFIG_PATHS["main"], DEFAULT_CONFIG).get("logging", log_config)
    env_level = log_config["level"] if log_config["level"] else "INFO"
    log_file = log_config.get("log_file", "dexlyn_trading.log")
    console_output = log_config.get("console_output", True)
    
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, env_level.upper()))
    
    # Update file handler if different file
    if console_output:
        if not any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers):
            logger.addHandler(logging.StreamHandler())
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)
    new_handler = logging.FileHandler(log_file, encoding='utf-8')
    logger.addHandler(new_handler)
    
    print("\n=== DEXLYN PERPETUALS TRADING BOT - COMPLETE FIELD CUSTOMIZATION ===\n")
    
    if args.generate_configs:
        generate_complete_config_files()
        print("🎉 All configuration files generated with complete examples!")
        print("📚 See field_reference.json for all available fields")
        return
    
    if args.generate_reference:
        generate_field_reference()
        print("✅ Field reference generated!")
        return
    
    # Check password
    password = os.environ.get("SUPRA_CLI_PASSWORD")
    if not password or password == "your_password_here":
        print("❌ Please set your password:")
        print("   export SUPRA_CLI_PASSWORD='your#password'")
        sys.exit(1)
    print("🔒 Password loaded from environment variable.")

    try:
        bot = AdvancedDexlynTradingBot(args.config_dir)

        if args.custom_config:
            bot.config_manager.load_all_configs(args.custom_config)
        print("🚀 Starting trading bot...")
        bot.run(args.strategy, args.cycles)
        
    except Exception as e:
        logging.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()