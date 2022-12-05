const PRODUCTS = [
    {
        id: 1,
        name: 'basil',
        price: 600,
        image: require('../assets/products/basil.jpg'),
        description: 'basil tres coll'
    },
    {
        id: 2,
        name: 'cactus',
        price: 600,
        image: require('../assets/products/cactus.jpg'),
        description: 'cactus a rose'
    },
    {
        id: 3,
        name: 'calathea',
        price: 2,
        image: require('../assets/products/calathea.jpg'),
        description: 'calathea soleil.'
    }
];

export function getProducts() {
    return PRODUCTS;
}

export function getProduct(id) {
    return PRODUCTS.find((product) => (product.id == id));
}

