/* ============================================================
   IntelliWealth – TypeScript Type Definitions
   ============================================================ */

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'investor' | 'advisor' | 'admin';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
}

export interface CustomerPayload extends RegisterPayload {
  role: 'investor' | 'advisor' | 'admin';
}

export interface Portfolio {
  id: string;
  customer_id: string;
  name: string;
  total_value: number;
  assets: Asset[];
  created_at: string;
  updated_at: string;
}

export interface Asset {
  id: string;
  portfolio_id: string;
  asset_name: string;
  asset_type: AssetType;
  quantity: number;
  purchase_price: number;
  current_value: number;
  created_at: string;
  updated_at: string;
}

export type AssetType = 'stocks' | 'gold' | 'mutual_funds' | 'crypto' | 'bonds' | 'cash';

export interface AllocationItem {
  asset_type: string;
  total_value: number;
  percentage: number;
  count: number;
}

export interface AllocationResponse {
  portfolio_id: string;
  total_value: number;
  allocations: AllocationItem[];
}

export interface PortfolioHistoryItem {
  id: string;
  portfolio_id: string;
  snapshot_date: string;
  value: number;
}

export interface Transaction {
  id: string;
  asset_id: string;
  type: string;
  amount: number;
  timestamp: string;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  environment: string;
  timestamp: string;
}
