import React, {ForwardRefExoticComponent, RefAttributes, useMemo} from "react";
import {MenuFoldOutlined, MenuUnfoldOutlined, UserOutlined} from "@ant-design/icons";
import DashboardLayoutHeaderStyle from "./DashboardLayoutHeaderStyle";
import {BasicProps} from "antd/lib/layout/layout";
import {Avatar} from "antd";
import Dropdown from "@/components/inputs/Dropdown/Dropdown";
import {useSelector} from "react-redux";
import {StateInterface, useAppDispatch} from "@/store/index";
import {authLocales} from "@/locales/authLocales";
import {useRouter} from "next/router";
import {logoutAction} from "@/store/auth/authAction";


interface DashboardLayoutHeaderProps {
    collapsed: boolean;
    setCollapsed: (value: boolean) => void;
    component: ForwardRefExoticComponent<BasicProps & RefAttributes<HTMLElement>>;
}

const DashboardLayoutHeader = (props: DashboardLayoutHeaderProps) => {
    const {lang} = useSelector((state: StateInterface) => state.locale);
    const {push} = useRouter();
    const {
        logout
    } = authLocales[lang];

    const dispatch = useAppDispatch();
    const doLogout = () => dispatch(logoutAction());
    const {collapsed, setCollapsed, component: Header} = props;
    const auth = useSelector((state: StateInterface) => state.auth);
    const fullname = useMemo(() => `${auth.user.first_name} ${auth.user.last_name}`, [auth.user.id]);
    const avatarMenuItems = [
        {
            label: <div onClick={doLogout}>{logout}</div>,
            key: '1',
        },
    ];

    if (!auth.isAuthenticated) {
        push('/auth');
        return null;
    }


    return (
        <DashboardLayoutHeaderStyle>
            <Header
                className="region-layout-background"
                style={{
                    padding: 0,
                }}
            >
                {React.createElement(collapsed ? MenuUnfoldOutlined : MenuFoldOutlined, {
                    className: 'trigger',
                    onClick: () => setCollapsed(!collapsed),
                })}

                <Dropdown menuItems={avatarMenuItems}>
                    <div className={'avatar-block'}>
                        <div className={'fullname'}>{fullname}</div>
                        <Avatar className={'user-avatar'} icon={<UserOutlined/>}/>
                    </div>
                </Dropdown>
            </Header>
        </DashboardLayoutHeaderStyle>
    );
};

export default DashboardLayoutHeader;
