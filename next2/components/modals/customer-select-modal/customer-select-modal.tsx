import React, { forwardRef, useImperativeHandle, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import { Button, Modal, Space, Table } from "antd";
import useDeferredPromise from "@/hooks/useDeferredPromise";
import { allCustomersRequest } from "@/api/backoffice/endpoints/customers/all";
import { useQuery } from "@tanstack/react-query";
import Search, { SearchByOption } from "@/ui/backoffice/search-with-filter";
import usePagination, { DEFAULT_PAGE_SIZE, PAGE_SIZE_OPTIONS } from "@/hooks/usePagination";
import useSearch from "@/hooks/useSearch";

interface ItemType {
  id: number;
}

export interface CustomerSelectModalResponseType {
  selected: boolean,
  item: null | ItemType
}

interface CustomerTableRecordType {
  id: number;
  full_name: string;
  age: null | number;
  email: string;
}

const { Column } = Table;

const MAIN_CACHE_KEY = "customers";

const searchByOptions: Array<SearchByOption> = [
  { label: "Full name", value: 'full-name' },
  { label: "Email", value: 'email' },
];

const CustomerSelectModal = (props, ref) => {
  const t = useTranslations("backoffice");
  const [open, setOpen] = useState<boolean>(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<Array<React.Key>>([]);
  const [selectedItem, setSelectedItem] = useState<null | CustomerTableRecordType>(null);

  const pagination = usePagination();
  const search = useSearch({
    onChange: () => {
      pagination.reset();
    }
  });

  const { defer, deferRef } = useDeferredPromise<CustomerSelectModalResponseType>();

  useImperativeHandle(ref, () => ({
    open() {
      setOpen(true);

      return defer().promise;
    }
  }));

  const { data, isFetching } = useQuery({
    enabled: open,
    queryKey: [MAIN_CACHE_KEY, { page: pagination.page, pageSize: pagination.pageSize, searchBy: search.debouncedSearchBy, query: search.debouncedQuery }],
    queryFn: () => allCustomersRequest(pagination.page, pagination.pageSize, search.debouncedSearchBy, search.debouncedQuery)
  });

  const dataSource: Array<CustomerTableRecordType> = useMemo(() => {
    return data?.data ? data.data.map(customer => ({
      id: customer.id,
      full_name: customer.full_name,
      age: customer.age,
      email: customer.email
    })) : [];
  }, [data]);

  const handleSelectedRowsChange = (selectedRowKeys: Array<React.Key>) => {
    setSelectedRowKeys(selectedRowKeys);
  };

  const handleModalOk = () => {
    closeModal();

    if (!selectedItem?.id) {
      deferRef.resolve({
        selected: false,
        item: null
      });
      return;
    }

    deferRef.resolve({
      selected: true,
      item: {
        id: selectedItem.id
      }
    });
  };

  const handleModalCancel = () => {
    closeModal();

    deferRef.resolve({
      selected: false,
      item: null
    });
  };

  const handleRowSelect = (record: CustomerTableRecordType) => {
    setSelectedItem(record);
  };

  const closeModal = () => {
    setOpen(false);
    setSelectedItem(null);
    setSelectedRowKeys([]);

    search.reset();
    pagination.reset();
  };

  return (
    <Modal
      title={t("select-customer")}
      open={open}
      width={720}
      className="max-w-lg"
      maskClosable={!isFetching}
      closable={!isFetching}
      cancelText={t("cancel")}
      okText={t("select")}
      okButtonProps={{
        disabled: !selectedItem
      }}
      onCancel={handleModalCancel}
      onOk={handleModalOk}
    >

      <div>
        <Search loading={isFetching}
                query={search.query}
                onQueryChange={search.setQuery}
                searchBy={search.searchBy}
                onSearchByChange={search.setSearchBy}
                searchByOptions={searchByOptions}
        />
      </div>

      <Table className="mt-4"
             bordered
             loading={isFetching}
             dataSource={dataSource}
             size={"small"}
             rowKey={"id"}
             pagination={{
               defaultPageSize: DEFAULT_PAGE_SIZE,
               pageSizeOptions: PAGE_SIZE_OPTIONS,
               onChange: (page: number, pageSize: number) => {
                 setSelectedItem(null);
                 setSelectedRowKeys([]);
                 pagination.set(page, pageSize);
               },
               current: pagination.page,
               pageSize: pagination.pageSize,
               total: data?.meta?.total
             }}
             rowSelection={{
               hideSelectAll: true,
               selectedRowKeys,
               onSelect: handleRowSelect,
               onChange: handleSelectedRowsChange,
               type: "radio"
             }}
      >
        <Column title="ID" dataIndex="id" />
        <Column title="Full name" dataIndex="full_name" />
        <Column title="Email" dataIndex="email" />
        <Column title="Age" dataIndex="age" />
      </Table>
    </Modal>
  );
};

export default forwardRef(CustomerSelectModal);
