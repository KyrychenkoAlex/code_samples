import React, { forwardRef, useImperativeHandle, useState } from "react";
import { useTranslations } from "next-intl";
import {Modal, Table } from "antd";
import useDeferredPromise from "@/hooks/useDeferredPromise";
import Search from "@/ui/backoffice/search-with-filter";
import usePagination, { DEFAULT_PAGE_SIZE, PAGE_SIZE_OPTIONS } from "@/hooks/usePagination";
import useSearch from "@/hooks/useSearch";
import useAllProductsQuery from "./queries/useAllProductsQuery";
import { ProductsTableRecord } from "./types";
import { Checkmark } from "@/components/backoffice/table";
import StylePreview from "@/components/backoffice/style-preview";

interface ItemType {
  id: number;
  name: string;
}

export interface CustomerSelectModalResponseType {
  selected: boolean,
  item: null | ItemType
}

const { Column } = Table;

const ProductSelectModal = (props, ref) => {
  const t = useTranslations("backoffice");
  const [open, setOpen] = useState<boolean>(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<Array<React.Key>>([]);
  const [selectedItem, setSelectedItem] = useState<null | ProductsTableRecord>(null);

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

  const allProductsQuery = useAllProductsQuery({
    enabled: open,
    page: pagination.page,
    pageSize: pagination.pageSize,
    searchBy: search.searchBy,
    searchQuery: search.query
  })

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
        id: selectedItem.id,
        name: selectedItem.name,
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

  const handleRowSelect = (record: ProductsTableRecord) => {
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
      title={t("select-product")}
      open={open}
      width={1024}
      className="max-w-lg"
      maskClosable={false}
      closable={!allProductsQuery.isFetching}
      cancelText={t("cancel")}
      okText={t("select")}
      okButtonProps={{
        disabled: !selectedItem
      }}
      onCancel={handleModalCancel}
      onOk={handleModalOk}
    >

      <div>
        <Search loading={allProductsQuery.isFetching}
                query={search.query}
                onQueryChange={search.setQuery}
                searchBy={search.searchBy}
                onSearchByChange={search.setSearchBy}
        />
      </div>

      <Table className="mt-4"
             bordered
             loading={allProductsQuery.isFetching}
             dataSource={allProductsQuery.dataSource}
             size={"small"}
             rowKey={"id"}
             pagination={{
               hideOnSinglePage: true,
               defaultPageSize: DEFAULT_PAGE_SIZE,
               pageSizeOptions: PAGE_SIZE_OPTIONS,
               onChange: (page: number, pageSize: number) => {
                 setSelectedItem(null);
                 setSelectedRowKeys([]);
                 pagination.set(page, pageSize);
               },
               current: pagination.page,
               pageSize: pagination.pageSize,
               total: allProductsQuery.pagination.total
             }}
             rowSelection={{
               hideSelectAll: true,
               selectedRowKeys,
               onSelect: handleRowSelect,
               onChange: handleSelectedRowsChange,
               type: "radio"
             }}
      >
        <Column title={t("active")}
                dataIndex="is_active"
                width={80}
                align="center"
                render={(_: any, record: ProductsTableRecord) => <Checkmark value={record.is_active}/>} />

        <Column title={t("style")}
                dataIndex="style"
                key="preview"
                align="center"
                width={80}
                render={(_: any, record: ProductsTableRecord) =>
                  <StylePreview background={record.style?.background}/>}
        />
        <Column title={t('name')} dataIndex={"name"} />
        <Column title={t('price')} align={"center"} dataIndex={"base_price_formatted"} />
        <Column title={t("bundle")}
                align={"center"}
                dataIndex={["product", "is_bundle"]}
                render={(_: any, record: ProductsTableRecord) =>
                  record.is_bundle ?
                    <div className={"flex items-center gap-2 justify-center"}>
                      <Checkmark value={true} />
                      <span>{record.bundle_products_count}</span>
                    </div> : null
                }/>
        <Column title={t("resource")} align="center" dataIndex={["resource", "name"]} />
        <Column title={t("entry-type")}
                align={"center"}
                dataIndex={["product", "has_entry_type"]}
                render={(_: any, record: ProductsTableRecord) =>
                  record.has_entry_type ?
                    <div className={"flex items-center gap-2 justify-center"}>
                      <Checkmark value={true} />
                      <span>{record.entry_type.name}</span>
                    </div> : null
                } />
      </Table>
    </Modal>
  );
};

export default forwardRef(ProductSelectModal);
