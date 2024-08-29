import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { allProductsRequest } from "@/api/backoffice/endpoints/products/all";
import { ProductsTableRecords } from "../types";
import { PaginationMeta } from "@/api/backoffice/types";
import { getDayjsInstanceFromBackendDateTimeFormat } from "@/utils/backoffice/date-time";
import { Dayjs } from "dayjs";

interface AllProductsQueryProps {
  enabled: boolean;
  page: number;
  pageSize: number;
  searchBy: string;
  searchQuery: string;
}

export const PRODUCTS_QUERY_KEY = "products"

const useAllProductsQuery = (props: AllProductsQueryProps) => {
  const { data, isFetching, refetch } = useQuery({
    enabled: props.enabled,
    queryKey: [PRODUCTS_QUERY_KEY, {
      page: props.page,
      pageSize: props.pageSize,
      searchBy: props.searchBy,
      searchQuery: props.searchQuery
    }],
    queryFn: () => allProductsRequest(props.page, props.pageSize, props.searchBy, props.searchQuery)
  });

  const dataSource: ProductsTableRecords = useMemo(() => {
    return data?.data ? data.data.map(product => ({
      ...product,
      updated_at: getDayjsInstanceFromBackendDateTimeFormat(product.updated_at) as Dayjs,
      created_at: getDayjsInstanceFromBackendDateTimeFormat(product.created_at) as Dayjs,
    })) : []
  }, [data]);

  const pagination: PaginationMeta = {
    total: data?.meta.total ?? 0
  };

  return {
    dataSource,
    pagination,
    isFetching,
    refetch
  };
};

export default useAllProductsQuery;
