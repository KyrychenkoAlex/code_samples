import NotFound from "@/components/NotFound/NotFound";
import styled from "styled-components";

const StyledNotFound = styled.div`
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
`;

export default function Auth() {
    return (
        <StyledNotFound>
            <NotFound/>
        </StyledNotFound>
    );
}
