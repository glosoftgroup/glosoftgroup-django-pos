import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import Pagination from 'react-js-pagination';
import Select2 from 'react-select2-wrapper';
import { fetchItems } from '../actions/action-items';

export class PaginateBlock extends Component {
  /*
   * This component renders pagination block
   * Props: Listed in PaginateBlock.propTypes below
   *        All props are fetch from redux
   *  Usage: <PaginateBlock />
   * */
  constructor(props) {
    super(props);
    this.state = {
      search: '',
      page: 5,
      activePage: 1,
      totalPages: 450,
      itemsCountPerPage: 10,
      show: false,
      edit: false,
      deleteUrl: 'url',
      item: {},
      category: '',
      pageSizes: [
        {'text': '5', 'id': '5'},
        {'text': '10', 'id': '10'},
        {'text': '20', 'id': '20'},
        {'text': '50', 'id': '50'},
        {'text': '100', 'id': '100'}
      ]
    };
  }
  static propTypes = {
    prop: PropTypes
  }

  componentDidMount() {
    this.props.fetchItems();
  }
  handleSelectChange = (e) => {
    this.setState({
      [e.target.name]: e.target.value
    });
    this.filterContent(this.state.search, null, e.target.value);
  }

  handlePageChange = (pageNumber) => {
    // console.log(`active page is ${pageNumber}`);
    this.setState({activePage: pageNumber});
    var search = this.state.search;
    this.filterContent(search, pageNumber);
  }

  onSelectChange = (e) => {
    this.setState({
      [e.target.name]: e.target.value
    });
    this.filterContent();
  }

  filterContent= (search, page) => {
    if (!page) {
      page = this.state.activePage;
    }
    var params = Object.assign({
      page_size: this.state.itemsCountPerPage,
      page: page
    });
    if (this.props.search) {
      params = { ...params, 'q': this.props.search.q };
    }

    if (this.props.date) {
      if (this.props.date.date) {
        params = { ...params, 'date': this.props.date.date };
      }

      if (this.props.date.date_from && this.props.date.date_to) {
        var dateFrom = this.props.date.date_from;
        var dateTo = this.props.date.date_to;
        params = { ...params, 'date_from': dateFrom, 'date_to': dateTo };
      }
    }
    if (this.props.mode) {
      params = { ...params, 'mode': this.props.mode.mode };
    }

    this.props.fetchItems(params);
  }

  render() {
    return (
      <div className={'no-print ' + this.props.openGraph.open}>
        <div className="row text-center mb-15">
                <div className="col-md-2 page-of mt-15 ml-15">
                <Select2
                    data={this.state.pageSizes}
                    onChange={this.onSelectChange}
                    value={ this.state.itemsCountPerPage }
                    name="itemsCountPerPage"
                    options={{
                      minimumResultsForSearch: -1,
                      placeholder: 'Select Page size'
                    }}
                />
                </div>
                <div className="col-md-7 page-of mt-15">
                    <Pagination
                        activePage={this.state.activePage}
                        itemsCountPerPage={this.state.itemsCountPerPage}
                        totalItemsCount={this.props.items.count}
                        pageRangeDisplayed={5}
                        onChange={this.handlePageChange}
                    />
                </div>
                <div className="col-md-2 page-of mt-15">Page {this.state.activePage} of {this.props.items.total_pages}</div>
            </div>
      </div>
    );
  }
}

PaginateBlock.propTypes = {
  items: PropTypes.array.isRequired,
  date: PropTypes.object.isRequired,
  fetchItems: PropTypes.func.isRequired,
  search: PropTypes.object.isRequired,
  mode: PropTypes.object.isRequired,
  openGraph: PropTypes.object.isRequired
};

const mapStateToProps = (state) => ({
  items: state.items,
  search: state.search,
  date: state.date,
  mode: state.mode,
  openGraph: state.openGraph
});

const mapDispatchToProps = (dispatch) => {
  return bindActionCreators({
    fetchItems: fetchItems
  }, dispatch);
};

export default connect(mapStateToProps, mapDispatchToProps)(PaginateBlock);
