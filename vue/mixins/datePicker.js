import {ref} from "vue";
import moment from "moment";

export default {
    data() {
        return {
            emptyDatePicker: ref([]),
            getDaysRange: (from, to) => {
                const date1 = new Date(from * 1000);
                const range = this.emptyDatePicker;
                const diffDays = this.getDiffDays(from, to);
                for (let i = 0; i < diffDays; i++) {
                    const newDate = new Date(date1);
                    newDate.setDate(date1.getDate() + i);
                    range.push(newDate);
                }
                return range;
            },

            getDiffDays (from, to) {
                return moment.unix(to).endOf('day').add(1, 'second').diff(moment.unix(from), 'days');
            }
        }
    }
}
