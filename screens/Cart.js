import React, { useEffect, useState, useContext } from 'react';
import { View, Text, Button, FlatList, StyleSheet } from 'react-native';
import { StripeProvider } from '@stripe/stripe-react-native';

import { CartContext } from '../CartContext';
import CheckoutScreen from '../CheckoutScreen';

export function Cart ({navigation}) {

  const {items, getItemsCount, getTotalPrice} = useContext(CartContext);
  
  function Totals() {
    let [total, setTotal] = useState(1);
    useEffect(() => {
      setTotal(getTotalPrice());
    });
    console.log(getTotalPrice());
    return (
       <View>
		   <View style={styles.cartLineTotal}>
		      <Text style={[styles.lineLeft, styles.lineTotal]}>Total</Text>
		      <Text style={styles.lineRight}>$ {total}</Text>
		   </View>
		   
		   <StripeProvider
			  publishableKey="pk_test_51MA9dsFGzyCFdYtCbIrqbYnh4CVLgHX1cfRSgHTcahN7Z2DlL4gBCgpGyhdibAlJItGyqYhFliyDMpJ3GyQKhqmk00S1Dfc42I"
			  merchantIdentifier="merchant.com.example"
			>
		    <CheckoutScreen
		    			amount={getTotalPrice()}/>
		   	</StripeProvider>
		  
		</View>
    );
  }

  function renderItem({item}) {
    return (
       <View style={styles.cartLine}>
          <Text style={styles.lineLeft}>{item.product.name} x {item.qty}</Text>
          <Text style={styles.lineRight}>$ {item.totalPrice}</Text>
       </View>
    );
  }
  
  return (
    <FlatList
      style={styles.itemsList}
      contentContainerStyle={styles.itemsListContainer}
      data={items}
      renderItem={renderItem}
      keyExtractor={(item) => item.product.id.toString()}
      ListFooterComponent={Totals}
    />
  );
}

const styles = StyleSheet.create({
  cartLine: { 
    flexDirection: 'row',
  },
  cartLineTotal: { 
    flexDirection: 'row',
    borderTopColor: '#dddddd',
    borderTopWidth: 1
  },
  lineTotal: {
    fontWeight: 'bold',    
  },
  lineLeft: {
    fontSize: 20, 
    lineHeight: 40, 
    color:'#333333' 
  },
  lineRight: { 
    flex: 1,
    fontSize: 20, 
    fontWeight: 'bold',
    lineHeight: 40, 
    color:'#333333', 
    textAlign:'right',
  },
  itemsList: {
    backgroundColor: '#eeeeee',
  },
  itemsListContainer: {
    backgroundColor: '#eeeeee',
    paddingVertical: 8,
    marginHorizontal: 8,
  },
});