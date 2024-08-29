import DashboardLayout from "@/components/layouts/DashboardLayout/DashboardLayout";

const Dashboard = () => {

    return (
        <div>Dashboard</div>
    );
};

Dashboard.getLayout = function getLayout(page) {
    return (
        <DashboardLayout>
            {page}
        </DashboardLayout>
    );
};

export default Dashboard;