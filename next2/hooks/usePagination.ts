import { useState } from "react";

const DEFAULT_PAGE = 1;
export const DEFAULT_PAGE_SIZE = 10;
export const PAGE_SIZE_OPTIONS = [DEFAULT_PAGE_SIZE, 20, 50, 100];

const usePagination = () => {
  const [page, setPage] = useState(DEFAULT_PAGE);
  const [pageSize, setPageSize] = useState(DEFAULT_PAGE_SIZE);

  const set = (page: number, pageSize: number) => {
    setPage(page);
    setPageSize(pageSize);
  };

  const reset = () => {
    setPage(DEFAULT_PAGE);
    setPageSize(DEFAULT_PAGE_SIZE);
  };

  return {
    page,
    setPage,
    pageSize,
    setPageSize,
    set,
    reset
  };
};

export default usePagination;
