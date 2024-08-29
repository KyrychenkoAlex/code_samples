import { Dayjs } from "dayjs";

export interface ProductsTableRecord {
  id: number;
  name: string;
  is_active: boolean;
  base_price_formatted: string;
  base_price: number;
  style: {
    id: number;
    background: string;
    color: string;
  }
  has_entry_type: boolean;
  entry_type: {
    id: number;
    name: string;
  },
  is_bundle: boolean;
  bundle_products_count: number;
  resource: {
    id: number;
    name: string;
  },
  updated_at: Dayjs;
  created_at: Dayjs;
}

export type ProductsTableRecords = Array<ProductsTableRecord>
