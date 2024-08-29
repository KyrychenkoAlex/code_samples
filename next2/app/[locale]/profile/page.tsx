"use client";

import { useLocale, useTranslations } from "next-intl";
import useAuth from "@/components/shop/auth/use-auth";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  EditProfileRequestDataType,
  getEditProfileFormRequest,
  putEditProfileRequest
} from "@/api/shop/endpoints/profile/edit";
import { Button, DatePicker, Form, Input, notification, Space, Spin, Typography } from "antd";
import { useEffect, useMemo } from "react";
import { DATE_DISPLAY_FORMAT } from "@/constants/shop";
import { getCurrentAgeFromDate, getDayjsInstanceFromBackendDateFormat } from "@/utils/shop/date-time";
import { getBackendAcceptedDateFormat } from "@/utils/shop/date-time";
import { Dayjs } from "dayjs";

const { Title, Text } = Typography;

const CACHE_MAIN_KEY = "customer";

const formItemLayout = {
  labelCol: {
    span: 4
  },
  wrapperCol: {
    span: 14
  }
};

interface FormDataType {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  birthdate: null | Dayjs;
}

export default function Page() {
  const queryClient = useQueryClient();

  const t = useTranslations("shop");
  const locale = useLocale();

  const [notificationAPI, contextHolder] = notification.useNotification();

  const { user } = useAuth();

  const customerId = user.id;

  const { isFetching, data } = useQuery({
    queryKey: [CACHE_MAIN_KEY, customerId],
    queryFn: () => getEditProfileFormRequest(customerId)
  });

  const [form] = Form.useForm();
  const birthdate = Form.useWatch("birthdate", form);

  const age = useMemo(() => getCurrentAgeFromDate(birthdate), [birthdate]);

  const initialValues = useMemo(() => (data ? {
    id: data.item.id,
    first_name: data.item.first_name,
    last_name: data.item.last_name,
    email: data.item.email,
    birthdate: getDayjsInstanceFromBackendDateFormat(data.item.birthdate)
  } : {}), [data]);

  useEffect(() => {
    form.resetFields();
  }, [initialValues]);

  const { mutate: submitForm, isPending } = useMutation({
    mutationFn: ({ customerId, requestData }: {
      customerId: number, requestData: EditProfileRequestDataType
    }) => putEditProfileRequest(customerId, requestData),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: [CACHE_MAIN_KEY] });

      notificationAPI.success({
        message: "Success!",
        description: data.message,
        placement: "topRight"
      });
    },
    onError: (data) => {
      notificationAPI.error({
        message: "Error!",
        description: data.message,
        placement: "topRight"
      });

      form.setFields(data.errors);
    }
  });

  const onFinish = (formData: FormDataType) => {
    const requestData: EditProfileRequestDataType = {
      first_name: formData.first_name,
      last_name: formData.last_name,
      birthdate: getBackendAcceptedDateFormat(formData.birthdate)
    };

    submitForm({ customerId, requestData });
  };

  return (
    <div>
      {contextHolder}
      <Title level={2}>{t("pages.profile.title")}</Title>
      {
        isFetching ? (
          <div>
            <Spin />
          </div>
        ) : (
          <Form
            {...formItemLayout}
            form={form}
            name="profile"
            onFinish={onFinish}
            layout="vertical"
            style={{ maxWidth: 600 }}
            initialValues={initialValues}
            scrollToFirstError
            disabled={isPending}
          >
            <Form.Item
              hidden
              name="id"
              label="id"
            >
              <Input />
            </Form.Item>

            <Form.Item
              name="first_name"
              label={t("form.first-name")}
              hasFeedback
              rules={[
                {
                  required: true,
                  message: "Please input first name!"
                }
              ]}
            >
              <Input placeholder={t("form.first-name")} autoComplete="off" />
            </Form.Item>

            <Form.Item
              name="last_name"
              label={t("form.last-name")}
              hasFeedback
              rules={[
                {
                  required: true,
                  message: "Please input last name!"
                }
              ]}
            >
              <Input placeholder={t("form.last-name")} autoComplete="off" />
            </Form.Item>

            <Space align="center" size="middle">
              <Form.Item
                className="flex-shrink-0"
                name="birthdate"
                label={t("form.birthdate")}
                hasFeedback
              >
                <DatePicker className="flex-shrink-0" format={DATE_DISPLAY_FORMAT} locale={locale}
                            style={{ width: 160 }} />
              </Form.Item>

              {age ? <Text>{age}</Text> : null}
            </Space>


            <Form.Item
              name="email"
              label={t("form.email")}
              hasFeedback
            >
              <Input placeholder={t("form.email")} autoComplete="off" disabled />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={isPending}>
                {t("form.submit")}
              </Button>
            </Form.Item>
          </Form>
        )}
    </div>
  );
}
