export const handlePromiseAllSettledResponse = (data:any) => {
    const res = data.map((item:any) => item.value);
    return res.filter(item => item!==null && item!==undefined);
};