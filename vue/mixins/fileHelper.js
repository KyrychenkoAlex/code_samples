import _get from "lodash/get.js";
import moment from "moment";

export default {
    methods: {
        downloadCsv(url, filename, mime = 'text/csv') {
            fetch(url, {method: 'GET'})
                .then(res => res.json())
                .then(res => {
                    const blob = new Blob([res], { type: mime});
                    const link = document.createElement('a');
                    link.href = window.URL.createObjectURL(new Blob([blob]));
                    link.setAttribute('download', filename);

                    document.body.appendChild(link);
                    link.click();
                    link.parentNode.removeChild(link);
                })
        },
        generateCsvFileName(model) {
            const uri = _get(this.$page.props.host.split('.'), '[0]', '');
            const m = moment().local();
            return `${uri}_${model}_${m.format('YYYY-MM-DD')}_${m.format('HH-MM')}.csv`
        }
    }
}
