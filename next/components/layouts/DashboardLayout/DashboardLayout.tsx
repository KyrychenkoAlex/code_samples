import {Layout} from 'antd';
import React, {useState} from 'react';
import DashboardLayoutStyle from "./DashboardLayoutStyle";
import DashboardLayoutSider from "@/components/layouts/DashboardLayout/DashboardLayoutSider/DashboardLayoutSider";
import DashboardLayoutHeader from "@/components/layouts/DashboardLayout/DashboardLayoutHeader/DashboardLayoutHeader";

const {Header, Sider, Content} = Layout;

const DashboardLayout = props => {
    const [collapsed, setCollapsed] = useState(false);

    return (
        <DashboardLayoutStyle>
            <Layout>
                <DashboardLayoutSider collapsed={collapsed} component={Sider}/>
                <Layout className="region-layout">
                    <DashboardLayoutHeader collapsed={collapsed} setCollapsed={setCollapsed} component={Header}/>
                    <Content className="region-layout-background">
                        {props.children}
                    </Content>
                </Layout>
            </Layout>
        </DashboardLayoutStyle>
    );
};

export default DashboardLayout;
