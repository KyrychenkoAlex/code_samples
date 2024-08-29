import React, { forwardRef, useImperativeHandle, useMemo, useState } from "react";
import { useTranslations } from "next-intl";
import {Modal, Table } from "antd";
import useDeferredPromise from "@/hooks/useDeferredPromise";
import { useQuery } from "@tanstack/react-query";
import Search, { SearchByOption } from "@/ui/backoffice/search-with-filter";
import usePagination, { DEFAULT_PAGE_SIZE, PAGE_SIZE_OPTIONS } from "@/hooks/usePagination";
import useSearch from "@/hooks/useSearch";
import { allUsersRequest } from "@/api/backoffice/endpoints/users/all";

interface ItemType {
  id: number;
}

export interface UserSelectModalResponseType {
  selected: boolean,
  item: null | ItemType
}

interface UserTableRecordType {
  id: number;
  full_name: string;
  email: string;
}

const { Column } = Table;

const MAIN_CACHE_KEY = "users";

const searchByOptions: Array<SearchByOption> = [
  { label: "Full name", value: 'full-name' },
  { label: "Email", value: 'email' },
];

const UserSelectModal = (props, ref) => {
  const t = useTranslations("backoffice");
  const [open, setOpen] = useState<boolean>(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<Array<React.Key>>([]);
  const [selectedItem, setSelectedItem] = useState<null | UserTableRecordType>(null);

  const pagination = usePagination();

  const search = useSearch({
    onChange: () => {
      pagination.reset();
    }
  });

  const { defer, deferRef } = useDeferredPromise<UserSelectModalResponseType>();

  useImperativeHandle(ref, () => ({
    open() {
      setOpen(true);

      return defer().promise;
    }
  }));

  const { data, isFetching } = useQuery({
    enabled: open,
    queryKey: [MAIN_CACHE_KEY, { page: pagination.page, pageSize: pagination.pageSize, searchBy: search.debouncedSearchBy, query: search.debouncedQuery }],
    queryFn: () => allUsersRequest(pagination.page, pagination.pageSize, search.debouncedSearchBy, search.debouncedQuery)
  });

  const dataSource: Array<UserTableRecordType> = useMemo(() => {
    return data?.data ? data.data.map(user => ({
      id: user.id,
      full_name: user.full_name,
      email: user.email
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

  const handleRowSelect = (record: UserTableRecordType) => {
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
      title={t("select-user")}
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
      </Table>
    </Modal>
  );
};

export default forwardRef(UserSelectModal);
