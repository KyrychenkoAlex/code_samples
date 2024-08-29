import {AuthTabs} from "@/components/AuthTabs/AuthTabs";
import DefaultLayout from "@/components/layouts/DefaultLayout/DefaultLayout";

export default function Auth() {
    return (
        <DefaultLayout>
            <AuthTabs/>
        </DefaultLayout>
    );
}
